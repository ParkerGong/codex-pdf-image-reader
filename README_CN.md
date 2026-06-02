# Codex PDF Image Reader

这是一个面向 Codex 的 PDF 图文辅助阅读 skill。它会把 PDF 转成一个紧凑的 reading pack：逐页文本、少量关键页渲染图、Markdown 报告、HTML 预览页和 JSON manifest。

核心原则很简单：先抽取全文文字，再只渲染真正承载证据的图表页。不要默认整篇 PDF 全量 rasterize；不要把 caption 当作视觉证据；写文献总结时区分 `text-checked`、`visual-checked`、`inferred` 和 `TODO visual verification`。

快速运行：

```bash
bash scripts/install.sh --with-deps
skills/codex-pdf-image-reader/scripts/run_pdf_image_reader.sh path/to/paper.pdf --pages 1,3,9-11
```

安装到 Codex：

```bash
bash scripts/install.sh --with-deps
```

依赖会安装到持久化用户环境 `${CODEX_HOME:-$HOME/.codex}/venvs/codex-pdf-image-reader`，避免每次阅读 PDF 都重新创建临时 venv。临时 venv 更适合一次性验证或隔离测试。
