# gouguoa-auto-test

gouguoa OA 系统的自动化测试仓库，基于本地搭建的测试环境（部署说明见 <https://blog.gougucms.com/home/book/detail/bid/3.html>）。
以 **Python + pytest** 为核心框架，覆盖接口自动化（登录 / 权限 / 上传 / 审批）与 UI 自动化（Selenium），目标是构建稳定、可维护、可工程化的测试套件。

> ⚠️ 仓库中**不含任何明文凭据**。所有环境相关配置（系统地址、数据库密码等）均通过环境变量注入，真实值存放在本地 `.env`（已被 `.gitignore` 忽略）或 CI Secrets 中，模板见 `.env.example`。

## 技术栈

| 领域 | 选型 |
| --- | --- |
| 测试框架 | pytest（含 `pytest-rerunfailures` 失败重试） |
| 接口测试 | requests + Session 封装 |
| UI 测试 | Selenium + Page Object 模式 |
| 验证码识别 | ddddocr（算式验证码 OCR 与计算） |
| 数据库校验 | PyMySQL |
| 配置管理 | pydantic-settings（环境变量 / `.env`，`GOUGUOA_` 前缀） |
| 测试报告 | Allure（`allure-pytest`） |

## 项目结构

```text
gouguoa-auto-test/
├── api_test/              # 接口测试模块
│   ├── test_cases/        # 接口测试用例
│   │   ├── conftest.py        # 接口夹具：已登录会话 / 验证码 / 数据库连接
│   │   ├── test_api_login.py  # 登录接口测试（含 OCR 验证码识别）
│   │   ├── test_rbac.py       # 权限控制（RBAC）接口测试
│   │   ├── test_upload.py     # 文件上传接口测试
│   │   └── test_approval_flow.py # 全流程请假审批测试
│   ├── helpers/           # 接口测试公共辅助
│   │   └── response.py        # 统一响应断言（assert_http_ok / assert_api_success）
│   └── data/              # 测试数据
│       ├── captcha_data/  # 验证码图片缓存
│       ├── upload_data/   # 上传测试文件
│       └── upload_data.csv
├── ui_test/               # UI 自动化模块
│   ├── conftest.py        # UI 测试夹具
│   ├── pages/             # 页面对象（Page Object）
│   │   ├── base_page.py       # 基础页面类（Selenium 封装）
│   │   └── login_page.py      # 登录页面
│   └── test_cases/
│       └── test_ui_login.py   # 自动化登录 UI 测试
├── utils/                 # 通用工具层
│   ├── api_auth.py        # 登录鉴权流程：下载验证码 / OCR / 提交登录
│   ├── test_data.py       # 测试数据加载：账号 / CSV 参数化
│   ├── captcha_solver.py  # OCR 验证码识别与算式计算
│   ├── db_util.py         # 数据库操作工具（PyMySQL 封装）
│   ├── file_reader.py     # 文件读取 / 账号解析工具
│   ├── request_util.py    # HTTP 请求封装（Session 支持、Cookie 持久化）
│   ├── logger.py          # 日志工具
│   └── __init__.py        # 统一导出入口
├── config/                # 环境配置
│   ├── conf.py            # 配置中心（pydantic-settings，GOUGUOA_ 前缀）
│   └── accounts.csv       # 测试账号数据
├── docs/                  # 项目文档 / 排查素材
├── reports/               # 测试报告产物（Allure temps / html）
├── .env.example           # 环境变量模板（提交入库，真实 .env 被忽略）
├── .gitignore             # Git 忽略规则
├── conftest.py            # pytest 全局夹具
├── pytest.ini             # pytest 配置（addopts / markers / testpaths）
├── run.py                 # 统一测试执行入口（运行 pytest 并生成 Allure 报告）
├── requirements.txt       # Python 依赖
└── README.md              # 项目说明
```

## 依赖与运行环境

- 推荐使用 **Python 3.8+**。
- 建议使用虚拟环境管理依赖：

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# 安装依赖
pip install -r requirements.txt
```

> 运行完整套件需具备：可用的 gouguoa 服务（或等价 Mock）、MySQL 实例、ddddocr 运行环境；UI 测试还需本机安装浏览器驱动（Selenium）。

## 配置（环境变量 / `.env`）

配置采用 **12-Factor / 企业实践**：所有配置项优先读取环境变量，未设置时回退到默认值；本地开发可把变量写入根目录 `.env`，生产 / CI 由流水线 Secrets 注入。变量统一以 `GOUGUOA_` 为前缀，由 `config/conf.py` 中的 `AppSettings`（`pydantic-settings`）加载与校验。

复制模板后在本地填写真实值（`.env` 已被忽略，**请勿提交**）：

```bash
cp .env.example .env
```

| 环境变量 | 说明 | 默认值 |
| --- | --- | --- |
| `GOUGUOA_BASE_URL` | 系统基础地址（不含结尾斜杠） | `http://192.168.198.133:81` |
| `GOUGUOA_DB_HOST` | 数据库主机 | `192.168.198.133` |
| `GOUGUOA_DB_PORT` | 数据库端口 | `3306` |
| `GOUGUOA_DB_USER` | 数据库用户 | `root` |
| `GOUGUOA_DB_PASSWORD` | 数据库密码 | `root` |
| `GOUGUOA_DB_NAME` | 数据库名 | `oa` |

> 约定：所有接口地址由 `BASE_URL` 拼接；验证码接口地址由 `get_captcha_url()` 动态生成（附时间戳防缓存），避免复用过期验证码。

## 运行测试

`pytest.ini` 中 `testpaths` 同时包含接口与 UI 用例。运行全部：

```bash
pytest
```

仅运行某一类（避免 UI 测试拉起浏览器）：

```bash
pytest api_test/            # 仅接口测试
pytest ui_test/             # 仅 UI 测试
pytest -m api               # 按标记运行接口测试
pytest -m ui                # 按标记运行 UI 测试
```

运行单个文件 / 用例：

```bash
pytest api_test/test_cases/test_api_login.py
pytest api_test/test_cases/test_api_login.py::test_login_with_ocr_captcha
```

可用标记（`pytest.ini` 中定义）：`smoke` / `login` / `regression` / `ui` / `api` / `rbac` / `auth` / `upload`。

## 测试报告（Allure）

项目使用 **Allure** 生成可视化报告（`pytest.ini` 已配置 `--alluredir=./reports/temps`）：

```bash
# 1) 运行测试并收集结果
pytest

# 2) 生成并打开 HTML 报告（需安装 Allure 命令行：https://allurereport.org/）
allure generate ./reports/temps -o ./reports/html --clean
allure open ./reports/html
```

也可直接通过 `run.py` 一键完成「运行测试 + 生成报告」，并支持命令行筛选范围：

```bash
python run.py                                      # 运行全部测试（读取 pytest.ini 配置）
python run.py --api                                # 仅运行接口测试
python run.py --ui                                 # 仅运行 UI 测试
python run.py --target api_test/test_cases/test_rbac.py   # 运行指定文件 / 目录
```

> `--api` / `--ui` / `--target` 三者互斥；均未指定时运行 `pytest.ini` 中配置的全部范围。`run.py` 会在测试结束后调用 `allure generate` 生成 HTML 报告，并以 pytest 退出码作为进程退出码。

## 核心功能与架构亮点

- **模块化工具层**（`utils/`）
  - `api_auth.py`：将「下载验证码 → OCR 识别 → 提交登录」收敛为 `fetch_captcha` / `solve_captcha` / `submit_login` / `login_via_session`，消除用例间重复逻辑。
  - `test_data.py`：通用 CSV 参数化加载器（`load_parametrized_csv` / `load_accounts` / `prepare_account`）。
  - `helpers/response.py`：统一接口断言 `assert_http_ok` / `assert_api_success`，避免散落的「`assert x, logger.error(...)`」反模式（日志返回 `None` 会导致断言信息丢失）。
  - `captcha_solver.py`：基于 ddddocr 的算式验证码识别与计算，含重试。
  - `request_util.py`：基于 Session 的 HTTP 封装（Cookie 持久化、登录态保持、防盗链 Token）。
- **测试分层清晰**：接口测试（登录 / RBAC 权限矩阵 / 文件上传 / 请假审批全流程）与 UI 测试（Selenium + Page Object）职责分离。
- **配置外置**：`pydantic-settings` 统一环境变量管理，密钥不入库，支持本地 `.env` 与 CI Secrets 两套注入。

## CI 集成（示例：GitHub Actions）

以下示例在 CI 中以环境变量注入配置，并**只跑接口测试**（`-m api`，避免 UI 测试依赖浏览器），最后上传 Allure 报告产物：

```yaml
name: CI

on: [push, pull_request]

jobs:
  api-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install allure-pytest
      - name: Run API tests
        env:
          GOUGUOA_BASE_URL: ${{ secrets.GOUGUOA_BASE_URL }}
          GOUGUOA_DB_HOST: ${{ secrets.GOUGUOA_DB_HOST }}
          GOUGUOA_DB_PORT: ${{ secrets.GOUGUOA_DB_PORT }}
          GOUGUOA_DB_USER: ${{ secrets.GOUGUOA_DB_USER }}
          GOUGUOA_DB_PASSWORD: ${{ secrets.GOUGUOA_DB_PASSWORD }}
          GOUGUOA_DB_NAME: ${{ secrets.GOUGUOA_DB_NAME }}
        run: pytest -m api
      - name: Upload Allure result
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: allure-results
          path: reports/temps
```

> 提示：CI 中真实地址与数据库密码请配置为仓库 **Secrets**，不要在 YAML 中明文出现。

## 贡献

欢迎贡献代码、测试用例与用例模板：

1. Fork 本仓库
2. 新建分支：`git checkout -b feature/xxx`
3. 提交并推送：`git commit -m "feat: 描述你的改动"` && `git push`
4. 发起 Pull Request，说明变更目的与验证方式

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

Copyright (c) 2026 F1ee987

## 联系方式

如有问题请联系维护者：@F1ee987
