# cookiecutter-fastapi

> 本文件约束模板仓库的维护；命令在仓库根目录执行。不编造生成项目的行为或验证结果。

## 项目

本仓库是 FastAPI 项目的 Cookiecutter 模板。修改模板会影响后续生成的项目；不要在仓库根目录直接启动应用。

## Layout

- `cookiecutter.json`：项目名称、标识、作者与版本等生成参数。
- `{{cookiecutter.application_slug}}/`：生成项目的文件模板，包含 FastAPI 应用、uv 配置与工程脚本。
- `hooks/`：生成前后的 Cookiecutter 钩子。

## Commands

需已安装 Cookiecutter。生成项目使用 Python 3.11+ 和 uv。

```bash
# 从当前本地模板生成项目，交互填写参数
cookiecutter . --output-dir /tmp/fastapi-projects

# 使用默认参数验证模板生成，输出目录需无同名项目
cookiecutter . --no-input --output-dir /tmp/fastapi-template-check
```

以下命令在生成的项目根目录执行：

```bash
uv sync
uv run scripts/dev.py
uv run scripts/test.py
uv run scripts/lint.py
```

`scripts/dev.py` 加载 `.env.dev` 并启动 8000 端口；测试脚本也加载 `.env.dev`，测试前需准备项目配置及数据库等外部服务。检查脚本会运行 mypy，并用 Ruff 修复和格式化代码。

## Boundaries

Always:
- 修改生成项目内容时编辑模板目录；直接修改生成副本不会修复模板。
- 保留 Jinja2 占位符及钩子的渲染语义；修改后用临时目录验证生成，避免破坏所有新项目。
- 命令以实际脚本和配置为准；根目录没有 Makefile，不使用 CONTRIBUTING.md 中的 make 命令。

Ask first:
- 删除或重命名生成参数、变更生成项目的公共 API 或新增依赖；这些变更会影响模板使用方。

Never:
- 不添加 `.trae` 配置或复制共享技能到模板中，避免生成项目携带重复规范。
- 不提交真实凭据或在日志中输出环境文件内容。
