# Codex PDF Image Reader

这是一个面向 Codex 的 PDF 图文辅助阅读 skill。它会把 PDF 转成一个紧凑的 reading pack：逐页文本、少量关键页渲染图、Markdown 报告、HTML 预览页和 JSON manifest。

核心原则很简单：先抽取全文文字，再只渲染真正承载证据的图表页。不要默认整篇 PDF 全量 rasterize；不要把 caption 当作视觉证据；写文献总结时区分 `text-checked`、`visual-checked`、`inferred` 和 `TODO visual verification`。

快速使用：

在 Codex 里直接说：

```text
从 https://github.com/ParkerGong/codex-pdf-image-reader 安装这个 Codex skill。
请把 Python 依赖安装到持久化 Codex venv。
然后使用 $codex-pdf-image-reader 阅读 path/to/paper.pdf，抽取文本并选择性渲染关键图表页。
```

指定页码时可以说：

```text
使用 $codex-pdf-image-reader 阅读 path/to/paper.pdf，并渲染第 1、3、9-11 页。
```

手动安装：

```bash
git clone https://github.com/ParkerGong/codex-pdf-image-reader.git
cd codex-pdf-image-reader
bash scripts/install.sh --with-deps
```

依赖会安装到持久化用户环境 `${CODEX_HOME:-$HOME/.codex}/venvs/codex-pdf-image-reader`，避免每次阅读 PDF 都重新创建临时 venv。临时 venv 更适合一次性验证或隔离测试。

手动运行：

```bash
skills/codex-pdf-image-reader/scripts/run_pdf_image_reader.sh path/to/paper.pdf --pages 1,3,9-11
```
