---
name: batch-image-processing
description: 使用本地 ImageMagick 完成单张或批量图片处理，包括格式转换（JPEG/JPG/PNG/WebP/HEIC/TIFF 等）、GIF 动画合成与拆帧、统一尺寸、裁剪、压缩、拼图、水印、调色、特效、透明通道、图像比较、元数据和高级像素运算。用户要求图片处理、调用 magick 或 ImageMagick 时使用；可组合全部官方命令行能力。
---

# 批量处理图片

直接使用本地 ImageMagick 执行用户任务。此技能覆盖官方全部命令行工具及选项，不以常用示例作为能力上限。适用于能执行本地命令并读取技能目录的 Agent；ImageMagick 是处理依赖，Python 3 仅用于文档检索和批处理示例。

## 工作流程

1. 确定输入范围、输出目录和目标结果。查看实际文件与图像信息；没有输入文件时询问位置。把用户的 `jepg` 识别为 JPEG 意图，但通过文件内容确认格式。说明影响结果的默认值；涉及不可推断的裁剪主体、帧顺序、目标大小或覆盖范围时询问必要问题。
2. 检查本机 `magick -version`；未安装时执行下方“自动安装与环境准备”，安装验证完成后继续原任务。再按任务查询 `magick -list format`、`delegate`、`policy`、`font` 或其他枚举。不要把官网支持清单等同于本机能力。
3. 选择工具与选项，按下方路由只读取相关参考。常用操作见 [recipes.md](references/recipes.md)；批量任务额外读 [batch.md](references/batch.md)。不熟悉的选项先查完整官方解释。
4. 默认在新的输出目录中保留原图，先处理代表性样本，再运行批量任务。覆盖原文件仅在用户要求时执行。已有目标文件不得静默替换；同名不同后缀转换时提前检查冲突。`mogrify` 默认会改写原文件。
5. 验证输出是否可解码，以及数量、格式、尺寸、透明通道和动画帧/时长是否符合请求。视觉相关处理查看样本图；完整结果检查不能只看命令退出码。记录失败项并给出实际输出路径、完成数量和必要限制。

## 自动安装与环境准备

用户调用本技能处理图片时，若电脑尚未安装 ImageMagick，Agent 应主动完成所需安装、环境生效和验证，再继续图片处理，不只返回安装教程或让用户手动执行。先简要告知准备安装；已有可用版本则复用，不为了使用技能自动升级或重装。

### 检测安装状态

- macOS / Linux：用 `command -v magick` 和 `magick -version` 检查；Windows PowerShell：用 `Get-Command magick -ErrorAction SilentlyContinue` 和 `magick -version` 检查。
- 找不到命令时先检查包管理器记录和标准安装位置，排除仅 PATH 未生效的情况。macOS 常见位置为 `/opt/homebrew/bin/magick`、`/usr/local/bin/magick`；Windows 根据安装记录定位 `magick.exe`。
- Linux 某些发行版仓库仍提供 ImageMagick 6。用 `identify -version`、`convert -version` 确认输出明确包含 `ImageMagick`；已有 v6 且能完成任务时读 `porting` 并调整调用。不要误用 Windows 系统自带的 `convert.exe`，也不要仅因缺少 `magick` 就重复安装 v6。

### 按操作系统安装

先识别系统与现有包管理器，只执行匹配的一条安装路径。Linux 使用 `/etc/os-release` 判断发行版；已是 root 时省略 `sudo`，否则按执行环境提供的提权流程运行。

| 环境 | 安装命令 |
| --- | --- |
| macOS，已有 Homebrew | `brew install imagemagick` |
| Windows，已有 WinGet | `winget install --id ImageMagick.ImageMagick --exact --source winget --silent --accept-source-agreements --accept-package-agreements` |
| Windows，无 WinGet 但已有 Chocolatey | `choco install imagemagick -y` |
| Debian / Ubuntu | 先 `sudo apt-get update`，成功后执行 `sudo apt-get install -y imagemagick` |
| Fedora / RHEL 系，仓库提供该包时 | `sudo dnf install -y ImageMagick` |
| Arch Linux | `sudo pacman -S --needed --noconfirm imagemagick`；不单独执行 `pacman -Sy` 造成部分升级 |
| openSUSE | `sudo zypper --non-interactive install ImageMagick` |
| Alpine Linux | `sudo apk add imagemagick` |

macOS 没有 Homebrew 时，Agent 从 <https://brew.sh/> 获取官方安装方式，将官方安装脚本下载到临时文件、检查后执行，再安装 ImageMagick；不要使用非官方镜像脚本。安装器若要求管理员交互，使用环境的审批或交互机制。Windows 没有可用包管理器时，从 <https://imagemagick.org/script/download.php#windows> 获取与系统架构匹配的官方安装程序，核对发布者/数字签名，按该安装器支持的参数安装；不猜测版本下载链接。其他系统或仓库无包时，从 <https://imagemagick.org/script/download.php> 查找适用的官方二进制或源码安装方式，优先用户目录安装，不覆盖已有系统版本。

安装所需网络访问或管理员权限受限时，主动发起执行环境支持的权限申请；不索取或代填用户密码，不绕过系统限制。只有必须由用户完成的授权、交互或网络条件阻止继续时，才说明具体阻塞与最小必要操作。不得把安装失败报告为成功，也不得反复重试相同失败命令。

### 生效、验证并继续原任务

1. 安装后刷新当前进程 PATH，或直接使用已定位的可执行文件绝对路径。Homebrew 可采用对应安装位置的 `brew shellenv`；Windows 可合并读取 Machine/User PATH 更新当前 PowerShell 的 `$env:Path`。不默认要求用户重启电脑或终端。
2. 执行 `magick -version`，确认确实为 ImageMagick；v6 使用经过确认的 `convert -version` 和 `identify -version`。检查任务需要的 `-list format` / `-list delegate`，不能仅凭包管理器成功退出判定可用。
3. 在新建临时目录中执行最小读写验证：`magick -size 2x2 xc:red /absolute/temp/probe.png`，再 `magick identify -format '%m %wx%h' /absolute/temp/probe.png`，结果应为 `PNG 2x2`；执行 `magick /absolute/temp/probe.png null:` 确认完整解码。v6 对应使用 `convert`、`identify`。仅清理本次生成的临时文件。
4. Python 3 仅在需要运行文档检索脚本或 Python 批处理时安装，优先复用现有解释器；Windows 可检查 `py -3`。官方快照也能直接读取，不为简单图片处理额外安装 Python。刷新官方快照时才需要 `curl`。
5. 仅当实际任务缺失相关能力时补装 delegate：例如 PDF/PS 的 Ghostscript、视频的 FFmpeg，使用对应系统的包管理器并验证具体格式样本。安装外部组件不保证当前 ImageMagick 编译包含相应 coder；继续检查格式支持，不自动放宽安全策略或安装所有可选依赖。
6. 环境验证通过后直接恢复用户的图片处理任务，并在最终结果中简要说明本次安装的组件与版本。

## 全部工具

| 调用 | 用途与选择条件 |
| --- | --- |
| `magick` | 主要入口：格式转换、所有图像操作、图像序列、绘图、合成、表达式；ImageMagick 7 不使用 `magick convert`。 |
| `magick-script` / `magick -script` | 原生命令脚本；不要当作 shell 脚本，先查脚本语法。 |
| `magick identify` | 文件识别、尺寸、帧、像素统计、详细属性和元数据。 |
| `magick mogrify` | 对多个输入应用同一操作；使用独立 `-path`，或已有明确原地修改要求。 |
| `magick montage` | 网格拼图、缩略图索引、标签、边框。 |
| `magick composite` | 两图合成、水印和混合；一般也可用 `magick ... -composite`。 |
| `magick compare` | 可视差异、误差指标、子图匹配。退出码 1 通常表示不同，并非执行失败。 |
| `magick stream` | 逐行输出原始像素组件，适合大图及原始像素数据。 |
| `magick conjure` | 执行 MSL XML 图像脚本；外来脚本须先检查其读写行为。 |
| `magick animate` | X server 上播放序列，不是生成 GIF 的必要工具。 |
| `magick display` | X server 上显示和交互编辑；无 X 环境时使用 Agent 图片预览。 |
| `magick import` | X server 窗口/屏幕捕获；不等同于 macOS、Windows 的通用原生截图。 |

完整逐工具文档、每个选项和相关专题见 [official-index.md](references/official-index.md)。这些是官方全文快照，不需要把全部内容同时载入上下文。

## 按能力检索

在技能目录中运行以下命令；从其他目录调用时使用脚本的绝对路径：

```sh
python3 scripts/official_docs.py read command-line-options resize
python3 scripts/official_docs.py read magick-script
python3 scripts/official_docs.py read defines
```

| 任务 | 官方页面及选项检索词 |
| --- | --- |
| 文件转换、压缩、质量、位深、多页文档、RAW | `formats`、`defines`、`webp`、`jp2`、`miff`；`quality`、`compress`、`depth`、`density`、`scene`、`adjoin`、`endian` |
| 缩放、裁剪、旋转、透视、形变、画布 | `command-line-processing`；`resize`、`thumbnail`、`resample`、`crop`、`extent`、`trim`、`rotate`、`distort`、`affine`、`shear`、`liquid-rescale` |
| GIF、动画 WebP、帧处理与序列运算 | `command-line-options`；`delay`、`loop`、`dispose`、`coalesce`、`layers`、`deconstruct`、`morph`、`duplicate`、`delete`、`reverse`、`insert`、`swap`、`evaluate-sequence`；视频另读 `motion-picture` |
| 拼图、合成、蒙版、透明、水印 | `montage`、`compose`、`composite`；`append`、`smush`、`alpha`、`channel`、`compose`、`composite`、`mask`、`clut`、`hald-clut` |
| 颜色、ICC、亮度对比度、直方图、量化 | `color`、`color-management`、`quantize`、`clahe`；`colorspace`、`profile`、`level`、`gamma`、`modulate`、`normalize`、`equalize`、`colors`、`dither`、`remap`、`threshold` |
| 去噪、模糊、锐化、卷积、形态学、特效 | `command-line-options`；`blur`、`bilateral-blur`、`unsharp`、`statistic`、`noise`、`convolve`、`morphology`、`edge`、`emboss`、`sketch`、`paint`、`polaroid`、`wave`、`vignette` |
| 文字、图形、标注、渐变与程序生成图片 | `magick-vector-graphics`、`gradient`、`color`；`draw`、`annotate`、`font`、`pointsize`、`fill`、`stroke`；`label:`、`caption:` 等伪格式见 `formats` |
| 分析、差异、连通域、颜色分割、像素数学 | `identify`、`compare`、`fx`、`connected-components`、`convex-hull`、`color-thresholding`；`metric`、`moments`、`evaluate`、`function`、`fft`、`ift`、`complex`、`integral` |
| 属性、EXIF、注释、ICC、命名表达式 | `escape`、`defines`；`format`、`print`、`set`、`strip`、`profile`、`auto-orient` |
| HDRI、多光谱、缓存、大图、并行与策略 | `high-dynamic-range`、`multispectral-imagery`、`stream`、`architecture`、`resources`、`security-policy`、`magick-cache`、`distribute-pixel-cache`、`openmp`、`opencl` |
| 脚本、加解密、版本兼容 | `magick-script`、`conjure`、`cipher`、`porting`；`encipher`、`decipher` |
| 未列出的任何能力 | 搜索 `official-index.md` 全部选项锚点，然后读取对应官方段落；查 `magick -help`、`magick TOOL -help` 和 `magick -list list` 获取本机支持。 |

## 执行要点

- 参数有顺序：读取前的 `-density` 决定矢量/PDF 栅格化；读取后的操作按顺序执行；设置会持续影响后续图像。括号用于分组，必要时用 `-respect-parentheses` 隔离设置；操作通道后用 `+channel` 复位。
- Shell 中引用路径、`640x480>`、`640x480^`、`!`、颜色 `#...`、表达式和帧选择器；括号转义为 `\(`、`\)`。批量动态参数优先 `subprocess.run([...], check=True)`，不用 `eval` 或 `shell=True`。数组避免 shell 展开，但 ImageMagick 自身仍解释特殊文件名和格式前缀。
- 照片先 `-auto-orient`，再缩放和裁剪。默认保留比例；“严格相同尺寸”还需确定留白或裁剪。不得默默拉伸。
- JPEG 不支持透明；转 JPEG 时明确底色并去除 alpha。GIF 有调色板与透明度限制；不要承诺保留全彩和半透明效果。`-quality` 含义与格式相关，不能保证固定文件体积。
- `-strip` 会删除 EXIF 和 ICC 等信息，不作为所有任务的默认步骤。需要去隐私元数据时先完成方向和色彩转换；印刷色彩转换需要正确输入/输出 ICC profile。
- 多帧/多页输入不得默默只取 `[0]`；先确认任务是首帧、全部拆分还是保留序列。GIF 编辑先 `-coalesce`，处理后再优化；验证优化后的合成画面与画布，不能要求差分帧都等于画布尺寸。
- PDF/PS 常依赖 Ghostscript，视频常依赖 FFmpeg，SVG/字体/HEIC 等取决于安装。策略拒绝时报告具体原因；不自动放宽 `policy.xml`。X 工具可能未编译进本机。
- 文字和拼图遇到字体枚举为空或默认字体失败时，检查本机字体文件并显式传入 `-font`；不要依赖固定字体名，也不要因此修改全局配置。
- 大图/长动画按实际资源使用 `-limit memory`、`-limit map`、`-limit disk`、`-limit time`，分批或顺序执行。像素缓存溢出会使用磁盘，检查可用空间。
- ImageMagick 擅长确定性图像操作，不具备通用语义抠图、生成式修复或 OCR 识别能力；遇到这些任务说明边界，不把简单阈值处理当作等价结果。

## 官方参考维护

官方来源为用户给定的 <https://imagemagick.org/command-line-tools/>，以及其工具、选项、格式和专题页面。快照日期见索引，原始文档版权与许可见 `references/official/license.html`。主技能和示例为中文，官方全文保留原文。

只有需要刷新技能参考时运行 `python3 scripts/official_docs.py refresh`；日常处理不需要联网或更新。脚本先下载并校验所有页面，再更新快照；网络代理失效且允许直连时可加 `--no-proxy`。参考描述的是官网版本，执行前以本机帮助、枚举和样本运行校验兼容性。ImageMagick 6 环境先读取 `porting`，不要盲目把系统同名 `convert` 当作 ImageMagick。
