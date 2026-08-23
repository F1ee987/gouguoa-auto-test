"""
文件上传接口测试。

用例数据来自 api_test/data/upload_data.csv：
    file_type, path, expected_result, description
其中 path 为相对于项目根目录的文件路径；expected_result 为期望的接口返回 code。
"""
import pytest
from pathlib import Path

from config.conf import FILE_UPLOAD, ROOT
from utils import Logger, RequestHandle, delete_cache, load_parametrized_csv

UPLOAD_DIR = Path(ROOT) / "api_test" / "data" / "upload_data"
UPLOAD_CSV = Path(ROOT) / "api_test" / "data" / "upload_data.csv"


def _ensure_dummy_files() -> None:
    """保证上传测试所需的占位文件存在（缺失时创建空文件，便于全新环境运行）。"""
    for ext in (".csv", ".txt", ".pdf"):
        target = UPLOAD_DIR / f"upload{ext}"
        if not target.exists():
            target.write_text(f"filetype={ext}", encoding="utf-8")


_ensure_dummy_files()

TEST_DATA, TEST_IDS = load_parametrized_csv(
    UPLOAD_CSV, data_columns=[0, 1, 2], id_column=3, min_fields=4
)


@pytest.mark.upload
@pytest.mark.parametrize("file_type, relative_path, expected_code", TEST_DATA, ids=TEST_IDS)
def test_upload(
    file_type: str, relative_path: str, expected_code: str,
    admin_api_login: RequestHandle, logger: Logger,
):
    """上传不同格式文件，校验返回 code 与预期一致。"""
    file_path = str(ROOT) + relative_path
    with open(file_path, "rb") as fp:
        response = admin_api_login.post(FILE_UPLOAD, files={"file": fp})

    assert response.status_code == 200
    try:
        body = response.json()
    except ValueError:
        pytest.fail(f"响应不是有效的 JSON: {response.text}")

    actual_code = str(body.get("code"))
    try:
        assert actual_code == str(expected_code), \
            f"预期结果：{expected_code}, 实际结果：{actual_code}, 消息：{body.get('msg')}"
        logger.info(f"✅ 文件上传成功 | 类型={file_type} | code={actual_code}")
    except AssertionError as e:
        logger.error(f"文件上传失败 | 类型={file_type} | {e}")
        raise
    finally:
        # 仅清理测试期间可能新增的占位文件，保留原始资源（如 png 截图素材）
        if not relative_path.endswith(".png"):
            delete_cache(file_path)
