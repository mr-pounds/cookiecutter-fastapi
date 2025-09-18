# Python 算法项目

## Python 版本说明

理论上 >3.10.X 都没问题，差异在于：
- 3.9.x 与 3.10.X 版本有内置运行时，有一些内置库，参考 [阿里云-Python 运行时说明](https://help.aliyun.com/zh/functioncompute/fc-3-0/user-guide/python)

经过验证后，FC部署将会先在本地构建镜像后，再上传到 FC 平台，无需做其他特殊处理。
  

## 依赖管理

默认使用 [uv](https://docs.astral.sh/uv/) 管理依赖，请先安装该工具。

```console
$ pip install uv
```

安装所有依赖：

```console
$ uv sync
```

然后激活虚拟环境：

```console
$ source .venv/bin/activate
```

请确保您的编辑器使用正确的 Python 虚拟环境，解释器路径为 .venv/bin/python。

### 添加依赖

如果要添加到 `prod` 环境的依赖。

```console
$ uv add <package-name> 
```

或者在 `pyproject.toml` 中添加，再执行 `uv sync`。

```toml
[project]
dependencies = [
    "pandas",
]
```


### 添加开发依赖

如果要添加到 `dev` 环境的依赖.

```console
$ uv add <package-name> --dev
```

或者在 `pyproject.toml` 中添加，再执行 `uv sync`。

```toml
[tool.uv]
dev-dependencies = [
    "pytest",
    "pytest-cov",
    "pre-commit",
]
```


## 测试

建议编写测试用例，运行方式：

```console
$ uv run ./scripts/test.py
```

测试基于 Pytest 框架，测试用例位于 `./app/tests/` 目录，可在此修改和添加测试。


### Test Coverage

测试运行后会生成  `htmlcov/index.html`，可在浏览器中打开查看测试覆盖率。


## pre-commit

模板仅集成了必要的三个hooks：`uv-lock`、`uv export`、`ruff`。环境部署时，安装依赖中，会包含 pre-commit（已经在开发依赖中）。如果没有该依赖，请先安装。

```console
$ uv add pre-commit --dev
```

`pre-commit` 依赖于 `.git`文件，因此要确保项目已初始化 Git 仓库。仓库初始化后，需要初始化配置化文件。

```console
$ uv run pre-commit install

# or
$ pre-commit install
```

你可以手动运行 pre-commit 来检查和格式化你的代码。例如，如果你想检查所有文件：
```console
$ uv run pre-commit run --all-files
```

### 更多 hooks

```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.4.0
  hooks:
    - id: check-added-large-files # 检查添加的大文件
    - id: check-toml # 检查 TOML 文件
    - id: check-yaml # 检查 YAML 文件
      args:
        - --unsafe
    - id: end-of-file-fixer # 检查并修复文件末尾的空行
      exclude: |
        (?x)^(
            frontend/src/client/.*|
            backend/app/email-templates/build/.*
        )$
    - id: trailing-whitespace # 检查并修复文件末尾的空格
      exclude: ^frontend/src/client/.*
- repo: local
  hooks:
    - id: isort # 排序导入
      name: isort
      stages: [commit]
      language: python
      entry: uv run isort {{cookiecutter.application_slug}}
      types: [python]
    - id: flake8 # 检查代码风格
      name: flake8
      stages: [commit]
      language: python
      entry: uv run flake8 {{cookiecutter.application_slug}}
      types: [python]
      exclude: setup.py
    - id: mypy # 类型检查
      name: mypy
      stages: [commit]
      language: python
      entry: uv run mypy
      types: [python]
      pass_filenames: false
    - id: pytest # 测试
      name: pytest
      stages: [commit]
      language: python
      entry: uv run pytest
      types: [python]
    - id: pytest-cov # 测试覆盖率
      name: pytest
      stages: [push]
      language: python
      entry: uv run pytest --cov --cov-fail-under=100
      types: [python]
      pass_filenames: false
```


## 部署

开发环境

```bash
# 脚本启动
uv run ./scripts/dev.py

# 手动启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env.dev --reload
```

生产环境
```bash
# 脚本启动
uv run ./scripts/prod.py

# 手动启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env.prod --workers 4 --timeout-keep-alive 900
```

## 其他注意事项

- `./doc/styles` 目录下的文件，是为 Vide Coding 提供的文档，包括一些示例。使用时，可引入文档内容来补充风格要求，确保AI能按照文档中的要求进行编码。
- `notebooks` 目录下用于存放算法测试和验证的文件，上传时尽量不要上传数据集或模型，请根据自己的习惯修改 `.gitignore`.
