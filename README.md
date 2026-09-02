# gouguoa-auto-test

gouguoa OA 系统的自动化测试仓库，基于本地搭建的测试环境（部署说明见 <https://blog.gougucms.com/home/book/detail/bid/3.html>）。
以 **Python + pytest** 为核心框架，覆盖**接口自动化**（登录 / 权限 / 上传 / 审批）与 **UI 自动化**（Selenium + Page Object），目标是一套稳定、可维护、可工程化的测试套件。

当前共 **27 条用例**：接口 18 条、UI 9 条，均以 Allure 输出报告。

> ⚠️ 仓库中**不含任何明文凭据**。所有环境相关配置（系统地址、数据库密码等）均通过环境变量注入，真实值存放在本地 `.env`（已被 `.gitignore` 忽略）或 CI Secrets 中，模板见 `.env.example`。

## 目录

- [技术栈](#技术栈)
- [测试覆盖范围](#测试覆盖范围)
- [项目结构](#项目结构)
- [依赖与运行环境](#依赖与运行环境)
- [配置与环境](#配置与环境)
- [运行测试](#运行测试)
- [测试报告](#测试报告)
- [架构设计与实现要点](#架构设计与实现要点)
- [CI 集成](#ci-集成)
- [已知限制与后续计划](#已知限制与后续计划)
- [贡献](#贡献)

## 技术栈

| 领域 | 选型 |
| --- | --- |
| 测试框架 | pytest（含 `pytest-rerunfailures` 失败重试） |
| 接口测试 | requests + Session 封装 |
| UI 测试 | Selenium + Page Object 模式 |
| 验证码识别 | ddddocr（算式验证码 OCR 与计算） |
| 数据库校验 | PyMySQL（UI 用例回查审批结果） |
| 配置管理 | pydantic-settings（环境变量 / `.env`，`GOUGUOA_` 前缀） |
| 测试报告 | Allure（`allure-pytest` + 命令行生成 HTML） |

## 测试覆盖范围

| 模块 | 用例文件 | 条数 | 覆盖场景 |
| --- | --- | --- | --- |
| 接口-登录 | `test_api_login.py` | 7 | 4 类角色正常登录；禁用账号 / 密码错误 / 空用户名登录失败（账号数据由 `config/accounts.csv` 参数化驱动） |
| 接口-权限 | `test_rbac.py` | 4 | 普通用户越权新增账号（期望 405）；管理员新增 / 修改用户；删除接口未开放（期望 405） |
| 接口-上传 | `test_upload.py` | 4 | pdf / txt / png 上传成功，csv 不支持上传失败；上传后清理（用例数据由 `upload_data.csv` 驱动） |
| 接口-审批流 | `test_approval_flow.py` | 3 | 员工提交请假 → 无权限节点审批被拒 → 人事经理审批通过 |
| UI-登录 | `test_ui_login.py` | 7 | 与接口同账号矩阵，通过登录后 URL 是否仍停留在登录页来校验登录态 |
| UI-审批全流程 | `test_ui_approve_flow.py` | 2 | 员工发起请假申请并提交；人事经理随机选择**通过 / 驳回**，并回查数据库 `check_status` 校验结果 |

## 项目结构

```text
gouguoa-auto-test/
├── api_test/                  # 接口测试模块
│   ├── test_cases/            # 接口测试用例
│   │   ├── conftest.py            # 接口夹具：按角色预登录的 Session / 数据库连接
│   │   ├── test_api_login.py      # 登录接口测试（含 OCR 验证码识别）
│   │   ├── test_rbac.py           # 权限控制（RBAC）接口测试
│   │   ├── test_upload.py         # 文件上传接口测试
│   │   └── test_approval_flow.py  # 请假审批全流程接口测试
│   ├── helpers/
│   │   └── response.py            # 统一响应断言（assert_http_ok / assert_api_success）
│   └── data/                  # 测试数据
│       ├── captcha_data/          # 验证码图片运行期缓存
│       ├── upload_data/           # 上传测试文件（缺失时用例自动创建占位文件）
│       └── upload_data.csv        # 上传用例参数化数据
├── ui_test/                   # UI 自动化模块
│   ├── conftest.py            # UI 夹具：会话级浏览器 + 按角色预登录的 driver
│   ├── pages/                 # 页面对象（Page Object）
│   │   ├── base_page.py           # 基础页面类（Selenium 封装：等待 / 输入 / 截图）
│   │   ├── login_page.py          # 登录页（OCR 验证码 + 登录重试）
│   │   ├── apply_page.py          # 发起审批页：选类型 → 填表单 → 选审批人 → 提交
│   │   └── approval_page.py       # 审批处理页：通过 / 驳回 + layui 弹层确认
│   └── test_cases/
│       ├── test_ui_login.py       # UI 登录测试
│       └── test_ui_approve_flow.py# 请假申请 + 审批全流程 UI 测试
├── utils/                     # 通用工具层
│   ├── api_auth.py            # 登录鉴权流程：下载验证码 / OCR / 提交登录
│   ├── test_data.py           # 测试数据加载：账号 / CSV 参数化
│   ├── captcha_solver.py      # OCR 验证码识别、字符纠偏与算式计算
│   ├── db_util.py             # 数据库操作工具（PyMySQL 封装）
│   ├── file_reader.py         # 文件读取 / 账号解析工具
│   ├── request_util.py        # HTTP 请求封装（Session、Cookie 持久化）
│   ├── logger.py              # 日志工具
│   └── __init__.py            # 统一导出入口
├── config/                    # 环境配置
│   ├── conf.py                # 配置中心（pydantic-settings，GOUGUOA_ 前缀）
│   └── accounts.csv           # 测试账号数据（角色 / 账号 / 密码 / 预期返回码）
├── docs/                      # 排查素材：OCR 识别失败时自动转储的验证码原图
├── reports/                   # 测试报告产物（Allure allure-results / html）
├── .env.example               # 环境变量模板（提交入库，真实 .env 被忽略）
├── .gitignore                 # Git 忽略规则
├── conftest.py                # pytest 全局夹具（计时器 / 日志 / 会话级数据库连接）
├── pytest.ini                 # pytest 配置（addopts / markers / testpaths）
├── run.py                     # 统一测试执行入口（运行 pytest 并生成 Allure 报告）
├── requirements.txt           # Python 依赖
└── README.md                  # 项目说明
```

## 依赖与运行环境

- 需要 **Python 3.9+**（依赖 `pydantic-settings` 2.x、`selenium` 4.x）。
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

运行完整套件还需具备：

| 依赖项 | 说明 |
| --- | --- |
| gouguoa 服务 | 接口与 UI 用例均访问真实系统（`GOUGUOA_BASE_URL`） |
| MySQL 实例 | 接口用例做数据准备，UI 用例回查审批状态 |
| Chrome 浏览器 | UI 用例使用 headless Chrome；Selenium 4.6+ 自带 Selenium Manager，无需手动下载驱动 |
| Allure 命令行 | 仅生成 HTML 报告时需要（<https://allurereport.org/>） |

## 配置与环境

配置采用 **12-Factor 实践**：所有配置项优先读取环境变量，未设置时回退到默认值；本地开发可把变量写入根目录 `.env`，生产 / CI 由流水线 Secrets 注入。变量统一以 `GOUGUOA_` 为前缀，由 `config/conf.py` 中的 `AppSettings`（`pydantic-settings`）加载。

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

**UI 运行相关**（仅影响 Selenium，不经过 `AppSettings`）：

| 环境变量 | 说明 | 默认值 |
| --- | --- | --- |
| `GOUGUOA_CHROMEDRIVER` | chromedriver 完整路径。不指定时会按顺序探测常见安装位置；都没命中才交给 Selenium Manager 联网解析，**内网 / 代理环境下会明显拖慢启动** | 自动探测 `D:/Python314/chromedriver.exe` 等 |
| `GOUGUOA_PAGE_LOAD_STRATEGY` | 页面加载策略。`eager` 等 DOMContentLoaded 即返回，每页可省 1~2s；页面渲染不稳定时设为 `normal` 回退 | `eager` |

> 约定：所有接口地址由 `BASE_URL` 拼接（集中定义在 `config/conf.py`）；验证码接口地址由 `get_captcha_url()` 动态生成（附时间戳防缓存），避免复用过期验证码。

## 运行测试

`pytest.ini` 中 `testpaths` 同时包含接口与 UI 用例。运行全部：

```bash
pytest
```

按标记筛选（标记在 `pytest.ini` 中注册，`api` / `ui` 已覆盖全部用例，即 18 + 9 条）：

```bash
pytest -m api               # 仅接口测试（18 条，不需要浏览器）
pytest -m ui                # 仅 UI 测试（9 条）
pytest -m "api and login"   # 组合筛选：接口登录用例
pytest -m "not ui"          # 排除 UI 用例
```

按目录 / 文件 / 单条用例运行：

```bash
pytest api_test/                                   # 仅接口测试
pytest ui_test/                                    # 仅 UI 测试
pytest api_test/test_cases/test_rbac.py            # 指定文件
pytest api_test/test_cases/test_api_login.py::test_login_with_ocr_captcha   # 指定用例
```

已注册标记：`smoke` / `login` / `regression` / `ui` / `api` / `rbac` / `auth` / `upload`。

> `pytest.ini` 默认开启 `--reruns 2 --reruns-delay 1`，用例失败会自动重试 2 次（OCR 识别偶发失败时不至于让整轮跑挂），该能力由 `pytest-rerunfailures` 提供。

## 测试报告

`pytest.ini` 已配置 `--alluredir=./reports/allure-results`，运行时自动采集结果：

```bash
# 1) 运行测试并收集结果
pytest

# 2) 生成并打开 HTML 报告（需安装 Allure 命令行）
allure generate ./reports/allure-results -o ./reports/html --clean
allure open ./reports/html
```

也可通过 `run.py` 一键完成「运行测试 + 生成报告」，并支持命令行筛选范围：

```bash
python run.py                                      # 运行全部测试（读取 pytest.ini 配置）
python run.py --api                                # 仅运行接口测试
python run.py --ui                                 # 仅运行 UI 测试
python run.py --target api_test/test_cases/test_rbac.py   # 运行指定文件 / 目录
```

> `--api` / `--ui` / `--target` 三者互斥；均未指定时运行 `pytest.ini` 中配置的全部范围。`run.py` 在测试结束后调用 `allure generate` 生成 HTML 报告，并以 pytest 退出码作为进程退出码（便于 CI 判断成败）。

## 架构设计与实现要点

### 工具层（`utils/`）

- `api_auth.py`：将「下载验证码 → OCR 识别 → 提交登录」收敛为 `fetch_captcha` / `solve_captcha` / `submit_login` / `login_via_session`，消除用例间重复逻辑。
- `captcha_solver.py`：基于 ddddocr 的算式验证码识别。含**误识别字符纠偏映射**（如 `>`→`7`、`)` 等 OCR 常见误判）、表达式合法性校验，识别失败时自动把原图转储到 `docs/` 便于复盘。
- `test_data.py`：通用 CSV 参数化加载器（`load_parametrized_csv` / `load_accounts` / `prepare_account`），账号与用例数据外置，新增场景只改 CSV。
- `db_util.py`：PyMySQL 封装，配合全局 `db_connect` 夹具做会话级连接复用，用于数据准备与结果回查。
- `helpers/response.py`：统一接口断言 `assert_http_ok` / `assert_api_success`，避免散落的「`assert x, logger.error(...)`」反模式（该写法中 `logger.error()` 返回 `None`，断言失败时拿不到任何信息）。

### UI 层：Page Object + 稳定性处理

UI 部分针对 gouguoa 的 **iframe + layui** 前端做了几处针对性处理，这几处也是最容易踩坑的地方：

| 问题 | 现象 | 处理方式 |
| --- | --- | --- |
| 主内容在 iframe 内 | 在顶层 document 定位「审批申请」永远找不到 | 操作前切到 `iframe[src='/home/index/main.html']`，再按 `data-href` 导航 |
| layui 弹层 id 动态递增 | 写死 `layui-layer3` 后，一旦多开一层就定位失败 | 按「可见 + z-index 最大」动态取当前弹层，再点其内 `.layui-layer-btn0`（确定） |
| `position: fixed` 元素可见性判断 | 用 `offsetParent !== null` 过滤会误判为不可见 | 改用 `getClientRects().length > 0` 判断 |
| 待办数据不属于当前登录人 | 只按 `check_status=1` 取记录，会挑到别人的待办，打开后没有审批按钮必然超时 | `ApprovalPage(driver, db, approver=...)` 用 `FIND_IN_SET(uid, check_uids)` 精确过滤 |
| OCR 偶发识别失败 | 登录随机失败，整条用例挂掉 | `login()` 内置最多 3 次重试；`pytest.ini` 另有失败重跑兜底 |

表单与下拉一律使用 `name` / `lay-filter` / `lay-value` 等语义化属性定位，不使用 `/html/body/...` 这类绝对 XPath。

### 其他

- **配置外置**：`pydantic-settings` 统一管理，密钥不入库，支持本地 `.env` 与 CI Secrets 两套注入。
- **测试分层**：接口与 UI 职责分离，共用 `utils/` 与 `config/`，避免重复实现。
- **失败可观测**：关键失败点自动附加 Allure 截图（登录失败、表单校验失败、审批结果异常）。

## CI 集成

以下示例在 CI 中以 Secrets 注入配置，并**只跑接口测试**（`-m api`，不依赖浏览器），最后上传 Allure 结果产物：

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
          path: reports/allure-results
```

> 提示：真实地址与数据库密码请配置为仓库 **Secrets**，不要在 YAML 中明文出现。
> `requirements.txt` 已包含 `allure-pytest` 与 `pytest-rerunfailures`，无需在 CI 中额外安装——缺少这两个插件时 pytest 会直接报 `unrecognized arguments`。

## 已知限制与后续计划

当前套件面向**真实部署环境**运行，在公共 CI 上直接跑还存在以下限制：

- **依赖真实环境**：用例直连 gouguoa 服务与 MySQL，没有 Mock Server；CI 跑接口测试需要先提供一个可访问的环境地址（或自建环境）。
- **会写入真实数据**：审批相关用例会真实提交 / 审批请假单，并消耗待审批记录。后续计划让用例自建数据（提交后清理），避免反复执行后无单可审。
- **UI 用例依赖浏览器**：CI 中默认只跑 `-m api`；如需跑 UI，需在 Runner 上安装 Chrome 并去掉 headless 相关限制。
- **尚未提供 Mock 模式**：计划引入可独立运行的 Mock 服务，使仓库在没有任何外部依赖时也能跑通冒烟用例，便于他人 clone 即跑。

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
