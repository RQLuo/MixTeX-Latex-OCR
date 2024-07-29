
![](demo/icon.png)
# MixTeX - 多模态 LaTeX-ocr CPU推理

MixTeX 是一款多模态 LaTeX 识别小程序，由我们自主研发，能够在本地离线环境下进行高效的 CPU 推理。无论是 LaTeX 公式、表格，还是混合文字，MixTeX 都能轻松识别，并且支持中英文双语处理。得益于强大的技术支持和优化设计，MixTeX 可以在没有 GPU 资源的情况下高效运行，适用于任何 Windows 电脑，极大地方便了用户的使用。
[![Paper](https://img.shields.io/badge/Paper-arxiv.2406.17148-white)](https://arxiv.org/abs/2406.17148) 
<a href="https://colab.research.google.com/github/RQLuo/MixTeX/blob/main/MixTex_Demo.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Community%20Space-blue)](https://huggingface.co/MixTex/ZhEn-Latex-OCR)
[![Demo Vedio](https://img.shields.io/badge/📺%20Demo-Vedio%20-white)](https://www.bilibili.com/video/BV1hS42197Vp/)

## 主要功能

- **LaTeX 公式识别**：精准识别复杂的 LaTeX 数学公式，确保数学表达的准确性。
- **表格识别**：高效处理并识别各类表格，生成对应的 LaTeX 表格代码。
- **混合文字识别**：同时处理包含文字、公式和表格的混合文本，保证识别结果的完整性和准确性。
- **中英文双语支持**：无论是中文还是英文，MixTeX 都能做到高精度识别，满足不同语言环境下的需求。

## 技术特点

- **本地离线推理**：无需联网，保证数据隐私安全，适合需要高保密性的用户场景。
- **轻量化设计**：启动程序文件仅 50 多 MB，便于快速部署和启动使用。
- **高效运行**：虽然模型文件大小为 300 MB，启动速度稍慢，但一旦加载后，运行速度极快，保证用户流畅的使用体验。
- **无需 GPU 资源**：在 CPU 上高效运行，适合所有 Windows 电脑，无需高配置硬件支持。

## 使用指南

1. **剪切板图片识别**：用户可以通过按下 `win+v` 开启剪切板功能，将需要识别的图片复制到剪切板。
2. **截图识别**：使用 Windows 自带的截图工具，通过键盘上的截屏按键进行截图，直接识别截图内容。

## 局限性

目前 MixTeX 只支持清晰打印字体下的中文和英文混合公式以及较为简单的表格识别。我们计划在后续版本中开放更多功能，包括支持手写公式和文字识别、多语言识别及复杂表格处理。

由于我们的模型训练数据集多为伪造生成，数据较为粗糙、单一且稀缺，识别效果和鲁棒性可能受到一定影响。我们将在后续逐步增加并完善在真实场景下的数据集训练，以获得更好的识别效果和鲁棒性。

## 用户

MixTeX 作为一款永久免费软件，承诺持续优化并保持本地离线运行，无任何广告干扰，为用户提供最优质的使用体验。用户可以加入我们的 QQ 群获取更多帮助和支持，与我们一起讨论和改进产品。

## 效果展示

MixTeX 在识别复杂文本方面表现出色，尤其是英文识别效果非常好，中文识别效果也不逊色。以下图片展示了 MixTeX 对复杂文本的识别效果：

![](demo/1.gif)

![](demo/3.png)

![](demo/2.png)


## 环境要求

MixTeX 使用 LaTeX 环境进行代码转换，建议使用以下 LaTeX 配置：

```latex
\documentclass{ctexart}
\usepackage{amssymb}
\usepackage{amsmath}
\usepackage{stmaryrd}
\usepackage{color}
```

## 更新日志

~~在使用过程中，您可能会遇到以下警告信息：`Error during OCR: Invalid image type. Expected either PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray, but got <class 'list'>.`~~
v1.0.1【已解决】**严重**：在运行软件时，无法复制文件，及其复制文件导致警告。

~~一直警告信息：`Error during OCR: Unable to infer channel dimension format.`~~
v1.0.2【已解决】**极端**：个别用户显示器太高级，色彩不是RGB，导致无法使用。

## 结语

MixTeX 致力于为用户提供最便捷、高效的多模态 LaTeX 识别工具，期待您的使用和反馈。如果您对 MixTeX 有任何建议或遇到问题，欢迎随时与我们联系。让我们一起努力，打造最优质的 LaTeX 识别工具！
