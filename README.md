# Batch Image Processing | 批量处理图片

**An AI agent skill for batch image conversion, resizing, compression, and GIF creation, powered by ImageMagick.**

**用自然语言让 AI Agent 批量转换图片格式、统一尺寸、压缩图片、制作 GIF。基于本地 ImageMagick，无需记忆命令行参数。**

[中文使用指南](#中文使用指南) · [English Guide](#english-guide) · [技能入口 / Skill](skills/batch-image-processing/SKILL.md) · [MIT License](LICENSE)

## 中文使用指南

### 这是什么？

`batch-image-processing` 是一个供 AI Agent 使用的图片处理技能。告诉 Agent 图片在哪里、想要什么结果，它就会检查环境，调用本地 ImageMagick 完成处理，并验证输出。

适合电商商品图、网站素材、设计交付、社交媒体图片和日常办公中的重复图片处理工作。它是技能指令和参考资料包，需要配合能够读取技能文件、访问本地图片并执行终端命令的 Agent 使用。

### 可以帮你做什么？

| 你的需求 | 技能可以完成的工作 |
| --- | --- |
| 批量转换图片格式 | JPEG/JPG 转 PNG、PNG 转 WebP、HEIC 转 JPG，以及 TIFF 等格式转换 |
| 批量统一图片尺寸 | 等比例缩放、固定宽高、居中裁剪、白边或透明留白 |
| 制作和编辑 GIF | 多图合成 GIF、设置顺序和速度、循环播放、拆帧、缩放和优化 |
| 压缩图片 | 调整质量、尺寸和编码参数，根据目标体积检查结果 |
| 拼图和缩略图 | 横向或纵向拼接、网格拼图、缩略图索引 |
| 水印和文字 | 添加图片水印、文字标注，调整位置与边距 |
| 透明背景和颜色 | 简单纯色背景透明化、透明图转白底、灰度、亮度与对比度调整 |
| 图片检查与清理 | 查看尺寸、帧数、元数据，按要求清理 EXIF，比较图像差异 |
| 进阶图像处理 | 蒙版、ICC 色彩管理、透视变换、形态学、像素表达式与多页图像处理 |

技能包含官方 **12 个命令行工具、309 个选项锚点和 45 份完整参考页面**，支持按需离线检索。以上是常用场景，不是功能上限；具体格式与操作是否可用，以本机版本、组件和安全策略为准。

### 安装技能

**方式一：让 Agent 帮你安装**

向支持本地技能安装的 Agent 发送：

```text
请从 https://github.com/Kz-Aven/batch-image-processing 安装批量处理图片技能。
技能位于仓库的 skills/batch-image-processing/ 目录。
请将这个完整目录安装到当前 Agent 的技能目录，检查 SKILL.md 能否被识别。
如果已有同名技能，请先比较版本，不要直接覆盖。
```

不同 Agent 的技能发现机制和安装位置可能不同。Codex 可使用 `${CODEX_HOME}/skills/`，未设置 `CODEX_HOME` 时通常为 `~/.codex/skills/`；其他 Agent 请使用其支持的技能目录。

**方式二：手动安装**

1. 克隆本仓库，或通过 GitHub 的 **Code → Download ZIP** 下载并解压。
2. 将仓库内整个 `skills/batch-image-processing/` 文件夹放到 Agent 的技能目录，保留所有子目录。
3. 按客户端要求刷新技能列表或开启新会话，确认出现 `batch-image-processing`。

```sh
git clone https://github.com/Kz-Aven/batch-image-processing.git
```

默认 Codex 目录下的入口应为 `~/.codex/skills/batch-image-processing/SKILL.md`。不要只安装 README，也不要把仓库根目录误当作技能目录。

### 没装 ImageMagick，也能开始吗？

可以。首次处理图片时，技能会指引 Agent 检测 ImageMagick；未安装时，选择适合 **macOS、Windows 或 Linux** 的安装方式，处理 PATH，完成图片读写验证，然后继续任务。

安装需要网络；系统要求管理员权限或人工交互时，Agent 会请求必要授权。已有可用版本会优先复用。Python 3 仅在需要相应辅助脚本时使用，PDF 或视频任务可能需要额外组件。

### 使用示例

支持 `$技能名` 的客户端可以用 `$batch-image-processing` 显式调用；其他客户端按其方式选择技能，再用自然语言描述任务。

**批量 JPEG 转 PNG**

```text
使用 $batch-image-processing，把 /path/to/photos 中的 JPG 和 JPEG 批量转成 PNG，
保存到 /path/to/output，保留原图。
```

**统一商品图尺寸**

```text
把 /path/to/products 中的图片统一成 1200×1200，保持比例，
不要裁掉商品，不足的部分补白边，输出到新的文件夹。
```

**多张图片制作 GIF**

```text
把 /path/to/frames 中的图片按文件名自然排序合成 GIF，
每帧 200 毫秒，无限循环，画布 800×600，保持比例并补白边。
```

**批量压缩网站图片**

```text
把 /path/to/images 中的图片转成 WebP，宽度不超过 1600 像素。
尽量让每张小于 300 KB；如果画质明显受损，请说明取舍。
```

**批量添加水印**

```text
给 /path/to/photos 中的图片加上 /path/to/logo.png 水印，
放在右下角，距离边缘 24 像素，保存到新的输出目录。
```

将示例路径替换成实际位置；Windows 可使用 `C:\Users\YourName\Pictures` 等路径。说明 **输入位置、目标效果、输出位置** 通常就足够了；GIF 再补充顺序和时长，统一尺寸时说明裁剪还是留白。

### 处理结果与原图保护

Agent 会报告输出位置、完成数量和失败项，并检查图片能否解码，以及格式、尺寸、帧数等是否符合要求。默认保留原图、写入新的输出目录，并检查重名冲突；需要覆盖原文件时请明确说明。

图片转换由本地 ImageMagick 执行，不需要专门的云端图片转换服务。Agent 平台是否上传图片用于视觉检查，取决于你使用的平台及其设置。

### 常见问题

**只能批量处理吗？** 单张图片也可以，直接指定文件即可。

**需要学习 ImageMagick 命令吗？** 不需要。描述目标效果即可，Agent 会选择命令和参数。

**支持所有图片格式吗？** 技能可检索完整官方格式参考，但实际读写能力取决于本机安装。Agent 会先检查，缺少组件时按任务处理。

**能做 AI 抠图、生成式修图或 OCR 吗？** 这些不是本技能的内置能力。纯色背景透明化不等同于语义抠图。

**为什么没有自动安装成功？** 网络限制、管理员权限或安装器交互可能阻止安装。Agent 应说明具体原因，不会把未完成的安装报告为成功。

## English Guide

### What Is Batch Image Processing?

`batch-image-processing` is an AI agent skill for editing individual images and automating repetitive image tasks with local ImageMagick commands. Tell your agent where your images are and what you need. It checks the environment, processes the files, and verifies the output.

Use it for product photography, website assets, design handoffs, social media images, and everyday office work. This repository contains skill instructions and reference materials. It requires an agent that can read skill files, access your images, and run terminal commands.

### Features

| What you need | What the skill can do |
| --- | --- |
| Batch image conversion | Convert JPEG/JPG to PNG, PNG to WebP, HEIC to JPG, and other formats such as TIFF |
| Batch image resizing | Resize proportionally, crop to fixed dimensions, or add white or transparent padding |
| GIF creation and editing | Turn images into animated GIFs, control frame order and timing, loop, extract frames, resize, and optimize |
| Image compression | Adjust quality, dimensions, and encoding settings, then check the actual file size |
| Collages and thumbnails | Join images horizontally or vertically and create grid contact sheets |
| Watermarks and text | Add image watermarks or text annotations with specified placement and margins |
| Transparency and color | Make simple solid backgrounds transparent, flatten transparency, and adjust grayscale, brightness, or contrast |
| Image inspection | Read dimensions, frame counts, and metadata; remove EXIF when requested; compare images |
| Advanced image processing | Use masks, ICC color profiles, perspective transforms, morphology, pixel expressions, and multipage images |

The bundled official reference snapshot covers **12 command-line tools, 309 option anchors, and 45 complete reference pages**, available for offline lookup. These examples do not limit the skill's scope. Available operations depend on your installed ImageMagick version, components, and security policy.

### Install the Skill

**Option 1: Ask your agent**

Send this request to an agent that supports installing local skills:

```text
Install the batch image processing skill from
https://github.com/Kz-Aven/batch-image-processing.
The skill is in skills/batch-image-processing/ inside the repository.
Install that complete directory into this agent's skill directory and verify
that SKILL.md is recognized. If a skill with this name already exists,
compare versions before replacing anything.
```

Skill discovery and installation paths vary by client. Codex can use `${CODEX_HOME}/skills/`, typically `~/.codex/skills/` when `CODEX_HOME` is unset. Use the documented skill location for other agents.

**Option 2: Install manually**

1. Clone this repository, or select **Code → Download ZIP** on GitHub and extract it.
2. Place the entire `skills/batch-image-processing/` folder in your agent's skill directory, including all subdirectories.
3. Refresh skill discovery or start a new session as required by your client. Check that `batch-image-processing` is available.

```sh
git clone https://github.com/Kz-Aven/batch-image-processing.git
```

For a default Codex installation, the entry point should be `~/.codex/skills/batch-image-processing/SKILL.md`. Install the skill folder, not just the README or the repository root.

### Automatic ImageMagick Setup

You do not need to install ImageMagick before your first task. The skill instructs your agent to detect it and, when missing, install it using an appropriate method for **macOS, Windows, or Linux**. The agent then resolves PATH issues, verifies image reading and writing, and resumes your request.

Installation requires network access and may require administrator approval or installer interaction. Existing working installations are reused. Python 3 is needed only for relevant helper scripts; tasks involving PDF or video may require additional components.

### Usage Examples

Use `$batch-image-processing` in clients that support explicit skill invocation. In other clients, select the skill using the client's supported mechanism and describe your task in natural language.

**Convert JPEG images to PNG**

```text
Use $batch-image-processing to convert all JPG and JPEG images in
/path/to/photos to PNG. Save them to /path/to/output and keep the originals.
```

**Resize product images to a consistent size**

```text
Make all images in /path/to/products exactly 1200×1200 pixels.
Keep their aspect ratios, do not crop the products, and add white padding.
Save the results in a new folder.
```

**Create an animated GIF from images**

```text
Create a GIF from the images in /path/to/frames using natural filename order.
Use 200 milliseconds per frame, loop forever, and fit each image into an
800×600 canvas with white padding while preserving its aspect ratio.
```

**Compress images for a website**

```text
Convert the images in /path/to/images to WebP with a maximum width of
1600 pixels. Try to keep each file below 300 KB, and explain any noticeable
quality tradeoffs.
```

**Add watermarks in bulk**

```text
Add /path/to/logo.png as a watermark to every image in /path/to/photos.
Place it in the bottom-right corner with a 24-pixel margin.
Save the results in a new output directory.
```

Replace the sample paths with your actual locations. Windows paths such as `C:\Users\YourName\Pictures` also work. Include the **input location, desired result, and output location**. For GIFs, specify order and timing; for fixed dimensions, specify cropping or padding.

### Output and Original Files

The agent reports output locations, completed files, and failures. It checks that generated images can be decoded and that the format, dimensions, and frame counts match your request. By default, it keeps originals, writes to a new output directory, and checks for filename collisions. Explicitly request in-place changes if needed.

Image conversion runs through local ImageMagick without a dedicated cloud image conversion service. Whether your agent platform uploads images for visual inspection depends on that platform and its settings.

### FAQ

**Can I process a single image?** Yes. Specify one file instead of a folder.

**Do I need to know ImageMagick commands?** No. Describe your desired result; the agent selects the commands and parameters.

**Does it support every image format?** The skill includes the full official format reference. Actual read and write support depends on your installation, which the agent checks before processing.

**Does it provide AI background removal, generative editing, or OCR?** These are not built-in capabilities. Making a solid background transparent is not the same as semantic background removal.

**What if automatic installation fails?** Network restrictions, permissions, or installer interaction can block setup. The agent should explain the specific issue rather than report an incomplete installation as successful.

## Documentation / 文档

| Resource / 资料 | Description / 说明 |
| --- | --- |
| [SKILL.md](skills/batch-image-processing/SKILL.md) | Agent instructions and automatic setup / 技能指令与自动安装流程 |
| [Common Recipes](skills/batch-image-processing/references/recipes.md) | Common image processing workflows / 常用图片处理流程 |
| [Batch Workflows](skills/batch-image-processing/references/batch.md) | Batch operations, filenames, and output handling / 批量执行、文件名与输出处理 |
| [Official Reference Index](skills/batch-image-processing/references/official-index.md) | Offline tools, options, and topic references / 离线工具、选项与专题索引 |
| [ImageMagick CLI](https://imagemagick.org/command-line-tools/) | Upstream command-line documentation / 上游官方命令行文档 |

技能指令和操作示例目前以中文编写，附带官方参考保留英文原文。本 README 提供中英文使用指南。

The skill instructions and workflow examples are currently written in Chinese; bundled official references retain their original English text. This README provides both Chinese and English user guides.

## Feedback / 问题反馈

通过 [GitHub Issues](https://github.com/Kz-Aven/batch-image-processing/issues) 反馈问题或提出使用场景。请附上操作系统、Agent 客户端、ImageMagick 版本、目标效果和错误信息；分享示例图片前移除敏感内容。

Use [GitHub Issues](https://github.com/Kz-Aven/batch-image-processing/issues) to report a problem or suggest a workflow. Include your operating system, agent client, ImageMagick version, expected result, and error message. Remove sensitive content before sharing sample images.

## License / 许可证

本仓库原创内容采用 [MIT License](LICENSE)。附带的 ImageMagick 官方文档保留其原有版权声明，并适用 [ImageMagick License](skills/batch-image-processing/references/official/license.html)。本项目是独立的 Agent 技能项目。

Original content in this repository is distributed under the [MIT License](LICENSE). Bundled ImageMagick documentation retains its original notices and is subject to the [ImageMagick License](skills/batch-image-processing/references/official/license.html). This is an independent agent skill project.
