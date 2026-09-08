# 批量执行

先枚举明确范围的输入，再规划所有输出；不把输出目录重新纳入输入，也不默认递归整个磁盘。区分两类任务：每张图片生成独立结果，与多张图片按顺序生成一个动画/拼图。`magick *.jpg output.png` 不等同于可靠的逐文件批处理。

## 每张输入对应一个输出

以下 Python 模板处理目录第一层 JPEG，保持完整原文件名再加 `.png`，避免 `photo.jpg`、`photo.jpeg` 合并成同一个目标。针对实际任务替换路径、筛选条件和参数数组。模板先验证全部输出不冲突，再写入新的目录；会完整解码验证输出、清理本次失败的临时文件，失败退出且打印具体项。

```python
from pathlib import Path
import re
import subprocess
import tempfile

source = Path('/absolute/input').resolve()
target = Path('/absolute/output').resolve()
if not source.is_dir():
    raise SystemExit(f'Input directory does not exist: {source}')
if source == target:
    raise SystemExit('Choose a separate output directory')

def natural_key(path):
    return tuple((0, int(part)) if part.isdigit() else (1, part.casefold())
                 for part in re.split(r'(\d+)', path.name))

files = sorted((p for p in source.iterdir()
                if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg'}),
               key=lambda p: (natural_key(p), p.name))
if not files:
    raise SystemExit('No matching input files')
outputs = [target / (p.name + '.png') for p in files]
names = [p.name.casefold() for p in outputs]
if len(names) != len(set(names)) or any(p.exists() for p in outputs):
    raise SystemExit('Output name collision; choose new output names/directory')
target.mkdir(parents=True, exist_ok=True)
failures = []
for src, dst in zip(files, outputs):
    try:
        # Neutral local names prevent ImageMagick filename expressions from
        # interpreting brackets, percent escapes or format prefixes in names.
        with tempfile.TemporaryDirectory(dir=target, prefix='.im-') as temporary:
            staged = Path(temporary)
            safe_input = staged / ('input' + src.suffix.lower())
            safe_input.symlink_to(src)
            result = staged / 'result.png'
            subprocess.run(['magick', str(safe_input), '-auto-orient', str(result)], check=True)
            subprocess.run(['magick', str(result), 'null:'], check=True)
            # Exclusive creation also protects against concurrent writers.
            with dst.open('xb') as output:
                try:
                    output.write(result.read_bytes())
                except BaseException:
                    dst.unlink()
                    raise
        print(f'OK {src} -> {dst}')
    except (OSError, subprocess.CalledProcessError) as error:
        failures.append((src, str(error)))
        print(f'FAILED {src}: {error}')
print(f'Completed {len(files) - len(failures)}/{len(files)}')
if failures:
    raise SystemExit(1)
```

此模板只针对已确认的单帧 JPEG。其他输入先识别帧数，再决定保留序列或命名拆帧，不能直接套用单输出逻辑。平台不支持符号链接时使用标准库 `shutil.copyfile` 将输入复制到中性临时文件名。大文件输出改用 `shutil.copyfileobj` 流式复制，避免整文件读入内存。

批量统一尺寸时，在 `-auto-orient` 之后插入所选几何参数；数组里的 `800x600>` 不再添加 shell 引号字符。使用 `magick identify` 验证目标宽高，并核对输出数量。

## 多图合成一个序列

先自然排序并确认顺序，再将显式路径列表展开到参数数组：

```python
command = ['magick', '-delay', '20', '-dispose', 'Background']
command += [str(path) for path in ordered_frames]
command += ['-auto-orient', '-resize', '640x480', '-background', 'white',
            '-gravity', 'center', '-extent', '640x480', '+repage',
            '-loop', '0', '-layers', 'Optimize', str(new_output)]
subprocess.run(command, check=True)
```

`ordered_frames` 和 `new_output` 必须来自已检查的输入和输出计划。文件名含 ImageMagick 特殊语法时同样暂存为中性文件名。读取现有 GIF 的帧与独立静态帧的 disposal 语义不同，先 coalesce 并保存时序信息。大量文件可能超出操作系统参数长度；分批生成 MIFF 中间序列再合并，或在安全策略允许时使用经过审核的原生脚本/文件列表，不通过放宽策略解决限制。

## 什么时候使用 mogrify

已验证的简单同参数批处理可以使用：

```sh
magick mogrify -path /absolute/new-output -format png /absolute/input/a.jpg /absolute/input/b.jpg
```

预先创建输出目录，并检查基础文件名冲突。`-path` 不会自动防止覆盖目标目录中的已有文件。没有 `-path` 的 `mogrify` 是原地操作，只适用于用户明确要求修改原文件的任务。
