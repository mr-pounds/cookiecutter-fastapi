# Python 算法项目

## Python 版本说明

理论上 >3.10.X 都没问题，差异在于：
- 3.9.x 与 3.10.X 版本有内置运行时，有一些内置库，参考 [阿里云-Python 运行时说明](https://help.aliyun.com/zh/functioncompute/fc-3-0/user-guide/python)
- 非 3.9.x 与 3.10.X 需要把所有依赖库都安装到项目根目录下 `pip install xxx -t .`
  
无论哪种，对于本地的虚拟环境管理都挺麻烦的。最好的方式是本地保留两个项目，一个用于开发，一个专门用于打包。


## 依赖管理

默认使用 [uv](https://docs.astral.sh/uv/) 管理依赖，请先安装该工具。

安装所有依赖：

```console
$ uv sync
```

然后激活虚拟环境：

```console
$ source .venv/bin/activate
```

请确保您的编辑器使用正确的 Python 虚拟环境，解释器路径为 .venv/bin/python。



## 测试

运行测试：

```console
$ uv run ./scripts/test.py
```

测试基于 Pytest 框架，测试用例位于 ./app/tests/ 目录，可在此修改和添加测试。


### Test Coverage

测试运行后会生成  `htmlcov/index.html`，可在浏览器中打开查看测试覆盖率。


#### 手动运行 pre-commit

你可以手动运行 pre-commit 来检查和格式化你的代码。例如，如果你想检查所有文件：
```bash
❯ uv run pre-commit run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
eslint...................................................................Passed
prettier.................................................................Passed
```

## 部署

开发环境

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env.dev --reload
```

生产环境
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env.prod --workers 4
```