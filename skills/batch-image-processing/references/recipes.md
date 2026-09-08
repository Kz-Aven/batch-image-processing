# 常用操作

以下为参数组合示例，不是需要用户手动执行的步骤。Agent 应替换为实际输入和新的输出路径并直接执行。Shell 示例按 POSIX shell 编写；Windows 可使用 Python 参数数组规避引号差异。不要对尚不存在的输入照抄命令。

## 检查与验证

```sh
magick -version
magick -list format
magick -list delegate
magick -list policy
magick identify -ping -format '%f %m %wx%h frames=%n\n' input.png
magick identify -verbose input.png
magick input.png null:
```

`-ping` 用于快速读头信息；最后一条执行完整解码检查，不能用 ping 替代。批量时记录每个输入的输出映射，逐个检查返回码和解码结果。`%n` 是序列图像总数，通常每帧重复打印。

## JPEG、PNG、WebP、HEIC 等格式转换

```sh
magick input.jpeg -auto-orient output.png
magick input.png -background white -alpha remove -alpha off -quality 90 output.jpg
magick input.png -quality 82 output.webp
magick input.png -define webp:lossless=true output.webp
magick input.heic -auto-orient output.png
```

HEIC 等先检查读取支持。PNG 无损编码的 `-quality` 不是 JPEG 质量百分比；减小 PNG 可使用 `-define png:compression-level=9`，需要减少颜色时另行评估 `-colors` 引入的损失。目标“低于 500 KB”需检测实际文件大小并逐步调整尺寸/质量，有停止条件；保留符合约束中质量较好的候选。

## 统一尺寸：先选几何语义

| 结果 | 参数组合 |
| --- | --- |
| 放入 800×600 边界框，保持比例 | `-resize '800x600'` |
| 只缩小，不放大 | `-resize '800x600>'` |
| 严格 800×600，完整图片加白边 | `-resize '800x600' -background white -gravity center -extent 800x600` |
| 严格 800×600，完整图片加透明边 | `-resize '800x600' -background none -gravity center -extent 800x600`，输出支持 alpha 的格式 |
| 严格 800×600，填满并裁剪 | `-resize '800x600^' -gravity center -extent 800x600` |
| 强制拉伸至 800×600，仅用户要求时 | `-resize '800x600!'` |
| 按宽度缩放 | `-resize 800x` |
| 按高度缩放 | `-resize x600` |

```sh
magick input.jpg -auto-orient -resize '800x600' -background white -gravity center -extent 800x600 output.png
magick input.jpg -auto-orient -gravity center -crop 600x600+0+0 +repage output.png
magick input.png -trim +repage output.png
magick input.jpg -auto-orient -rotate 90 output.jpg
```

裁剪后 `+repage` 清除虚拟画布偏移。中心裁剪只是已告知用户的默认值，主体保留要求需要查看图片并调整位置。`-density 300` 单独改变打印密度，不会把现有位图变成更高分辨率。

## 多张图片合成一个 GIF

需要确定：输入列表和顺序、每帧时长、循环次数、统一画布和背景。没有其他偏好时说明采用自然文件名排序、每帧 200 ms、无限循环、保持比例加边；画布尺寸按用户目标或首张定向后的尺寸确定。

```sh
magick -delay 20 -dispose Background frame1.png frame2.png frame3.png \
  -auto-orient -resize '640x480' -background white -gravity center -extent 640x480 \
  +repage -loop 0 -layers Optimize output.gif
magick identify -format 'frame=%s size=%wx%h page=%g delay=%T dispose=%D\n' output.gif
magick output.gif -coalesce -format '%wx%h\n' info:
```

`-delay` 单位是 1/100 秒，20 表示 200 ms。`-loop 0` 是无限循环。上例适用于独立完整静态帧；含透明或已有动画输入时先确认合成和 disposal 语义，不能默认复制此设置。把优化前后结果 coalesce 后比较视觉，确认没有残影、帧错位和意外停顿。

可将 `-delay` 放在特定输入前，为后续帧指定不同时长。`-set delay` 会覆盖已有时长，只在确实要统一速度时使用。自然排序不能只靠 shell glob：`1,2,10` 通常会被排成 `1,10,2`。

## GIF 拆帧、缩放、优化与格式转换

```sh
magick input.gif -coalesce frames/frame-%04d.png
magick input.gif -coalesce -resize '480x480>' -layers Optimize output.gif
magick input.gif -coalesce -layers Optimize output.gif
magick input.gif -coalesce -quality 85 output.webp
magick 'input.gif[0]' cover.png
```

创建新的 `frames` 输出目录。首帧命令仅适用于明确要求封面的情况。拆帧 PNG 不携带原动画时序，需要同步记录 delay/disposal/loop 信息才能精确重建。动画 WebP 的支持和时长需实测。

## 拼图、文字、水印与透明

```sh
magick left.png right.png +append horizontal.png
magick top.png bottom.png -append vertical.png
magick montage -font /absolute/path/to/font.ttf a.jpg b.jpg c.jpg d.jpg -auto-orient -thumbnail 240x180 \
  -tile 2x2 -geometry +12+12 -background white contact-sheet.png
magick input.jpg watermark.png -gravity southeast -geometry +24+24 -compose over -composite output.jpg
magick input.png -fuzz '5%' -transparent white output.png
magick -list font
```

简单白底透明化会同时影响主体中的近白像素，不能当作语义抠图。`montage` 即使没有显式标签也可能尝试加载默认字体；如果字体枚举为空或报 `unable to read font`，给 `-font` 指定实际系统字体文件，无需修改全局字体配置。macOS 可检查 `/System/Library/Fonts/`，Windows 检查系统 Fonts 目录，Linux 可用 `fc-match` 查找；不要把示例路径当作跨平台常量。文字使用实际存在、覆盖目标文字的字体路径：

```sh
magick input.png -font /absolute/path/to/font.ttf -pointsize 36 -fill white \
  -gravity south -annotate +0+24 '示例文字' output.png
```

用 `caption:` 实现指定宽度换行，`label:` 用于单行；从官方 `formats` 与 `escape` 查询文本转义。用户文本中的 `%[...]` 等可能被 ImageMagick 展开，动态文本先确认按字面输出的处理方式。

## 调色、锐化、模糊、元数据

```sh
magick input.jpg -auto-orient -colorspace Gray output.png
magick input.jpg -brightness-contrast 10x5 output.jpg
magick input.jpg -unsharp 0x1+1+0.05 output.jpg
magick input.png -blur 0x4 output.png
magick input.jpg -auto-orient -colorspace sRGB -strip output.jpg
```

最后一条适合已确认色彩来源的常规图片隐私清理；`-colorspace sRGB` 不是通用 ICC 转换的替代。如果用户要求准确 CMYK/广色域转换，使用实际 ICC 文件配合 `-profile`，先读 `color-management`。

## 比较和高级处理

```sh
magick compare -metric RMSE before.png after.png difference.png
magick input.png -morphology Dilate Disk:2 output.png
magick input.png -fx '1-u' output.png
magick -size 640x480 gradient:white-black gradient.png
```

`compare` 的指标在 stderr；0 表示相同、1 表示不同，其他退出码按错误处理，并检查 stderr。有损转换不能用“像素完全相同”作为成功条件。形态学、FX、FFT、透视、蒙版、连通域等任务从官方段落获取参数细节，再小图验证。

## PDF / 多页 TIFF / SVG

```sh
magick -density 150 input.pdf pages/page-%04d.png
magick page1.png page2.png -adjoin output.tiff
magick -background none -density 192 input.svg output.png
```

读取 PDF 常依赖 Ghostscript 和策略允许；页面较多时分批读取已确定的页面范围，例如 `'input.pdf[0-9]'`。PDF 写入通常是栅格图封装，不承诺保留原 PDF 的文本/矢量。SVG 渲染因 delegate、字体与外链不同可能变化，查看实际结果。
