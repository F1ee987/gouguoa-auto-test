# gouguoa-auto-test

这是 gouguoa 的自动化测试仓库，基于本地搭建测试环境系统，相关系统部署请转到https://blog.gougucms.com/home/book/detail/bid/3.html，
使用 Python + pytest 作为主要测试框架，目标是构建稳定、可维护的接口与 UI 自动化测试套件。

> 注意：请勿在仓库中提交明文凭据或敏感信息，推荐使用环境变量或 CI Secrets 管理密钥与密码。

## 项目结构
```text
gouguoa-auto-test/
├── api_test/              # 接口测试模块
│   ├── test_cases/        # 接口测试用例
│   │   ├── conftest.py    # 接口测试夹具
│   │   ├── test_login_for_api.py  # 登录接口测试（含OCR验证码识别）
│   │   ├── test_rbac.py   # 权限控制接口测试
│   │   ├── test_upload.py # 文件上传接口测试
│   │   └── reports/       # 接口测试报告
│   └── data/              # 测试数据
│       ├── captcha_data/  # 验证码图片缓存
│       ├── upload_data/   # 上传测试文件
│       └── upload_data.csv
├── ui_test/               # UI自动化模块
│   ├── conftest.py        # UI测试夹具
│   ├── pages/             # 页面对象模式
│   │   └── base_page.py   # 基础页面类（Selenium封装）
│   └── test_cases/        # UI测试用例
├── utils/                 # 通用工具类
│   ├── __init__.py
│   ├── captcha.py         # OCR验证码识别与计算
│   ├── db_util.py         # 数据库操作工具
│   ├── logger.py          # 日志工具
│   ├── reader.py          # CSV/文件读取工具
│   └── request_util.py    # HTTP请求封装（Session支持）
├── config/                # 配置文件
│   ├── conf.py            # 环境配置（URL、数据库、路径）
│   └── accounts.csv       # 测试账号数据
├── docs/                  # 项目文档
├── reports/               # 测试报告（pytest-html）
├── .gitignore             # Git 忽略规则
├── conftest.py            # pytest 全局夹具 (Fixture)
├── pytest.ini             # pytest 配置文件
├── run.py                 # 测试执行入口
├── requirements.txt       # Python 依赖
└── README.md              # 项目说明
```
## 依赖与运行环境

- 推荐使用 Python 3.8+（或与项目中指定版本一致）。
- 建议使用虚拟环境管理依赖：

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# 安装依赖（requirements.txt）
pip install -r requirements.txt
```


## 使用 pytest 运行测试

```bash
# 运行全部测试
pytest

# 运行接口测试
pytest api_test/

# 运行 UI 测试
pytest ui_test/

# 运行单个测试文件(示例)
pytest api_test/test_cases/test_login_for_api.py

# 运行特定测试用例
pytest api_test/test_cases/test_login_for_api.py::test_by_orc_captcha
```

生成的报告默认输出到 `./reports/report.html`（由 pytest.ini 的 --html 参数控制）。

## 关于 run.py

`run.py` 为测试执行入口脚本，会调用 `pytest.main()` 执行所有测试。

## 核心功能

### OCR 验证码识别
项目使用 `utils/captcha.py` 实现 OCR 验证码自动识别，支持：
- 验证码图片下载与缓存（`api_test/data/captcha_data/`）
- 算式验证码识别与计算（如 `15+3=18`）
- 识别失败自动重试机制

### 会话管理
`utils/request_util.py` 提供基于 Session 的 HTTP 请求封装，支持：
- Cookie 持久化
- 自动化登录状态保持
- 防盗链 Token 处理

## 配置与敏感信息管理

- 推荐使用 `.env` 或专门的配置文件（例如 config.yml）保存环境相关配置，并把敏感信息加入 `.gitignore`。
- 在 CI（例如 GitHub Actions）中使用 Secrets 管理凭证。

示例环境变量：

```bash
export DB_PASSWORD=root
export OA_BASE_URL=项目IP地址
```

## CI 集成（示例：GitHub Actions）

下面是一个简单的 GitHub Actions 流程示例（按需修改 Python 版本和安装命令）：

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: pytest
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: test-report
          path: reports/report.html
```

## 报告与日志

推荐使用 Allure、pytest-html 等工具生成更丰富的测试报告，并将 reports 目录作为构建产物上传保留执行记录。

## 贡献

欢迎贡献代码、测试用例与用例模板：

1. Fork 本仓库
2. 新建分支：git checkout -b feature/xxx
3. 提交并推送：git commit -m "feat: 描述你的改动" && git push
4. 发起 Pull Request，说明变更目的与验证方式

## 许可证

该仓库当前未指定具体开源协议。若需要公开发布，请添加 LICENSE 文件（例如 MIT、Apache-2.0 等）。

## 联系方式

如有问题请联系维护者：@F1ee987
