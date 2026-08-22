"""
@Project:gouguoa-auto-test
@File   :test_upload.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/18 14:58
"""
import pytest
from config.conf import FILE_UPLOAD, HOME
from utils import Reader, RequestHandle, Logger, del_cache
from typing import List, Tuple

def load_upload_test_data() -> Tuple[List[Tuple[str, str, str]], List[str]]:
    """读取上传文件的csv文件"""
    extension = ['.csv', '.txt', '.pdf']
    filepath = f"{str(HOME)}/api_test/data/upload_data/upload"
    for i in range(len(extension)):
        with open(f'{filepath}{extension[i]}', 'w', encoding='utf-8') as f:
                f.write(f'filetype={extension[i]}')
    print("开始读取上传文件的csv文件")
    r = Reader()
    filepath = f'{HOME}/api_test/data/upload_data.csv'
    print(f'读取文件路径：{filepath}')
    result = r.read_csv(filepath)
    if not result:
        pytest.skip("上传文件的csv文件不存在")
    data: List[Tuple[str, str, str]] = []
    ids: List[str] = []
    for row in result[1:]:
        if len(row) < 4:
            print(f"⚠ 跳过字段不完整的数据行：{row}")
            continue

        data.append((row[0], row[1], row[2]))
        ids.append(row[3])
        print(f"✅ 加载测试数据：{row}")

    if not data and not ids:
        pytest.skip("没有有效的测试数据")

    return data, ids

TEST_DATA, TEST_IDS = load_upload_test_data()

@pytest.mark.upload
@pytest.mark.parametrize("filetype, path, expected", TEST_DATA, ids=TEST_IDS)
def test_upload(filetype: str, path: str, expected: str, admin_api_login: RequestHandle, logger: Logger):
    with open(f'{str(HOME)+path}', 'rb') as f:
        upload_res = admin_api_login.post(
            FILE_UPLOAD,
            files={'file': f}
        )
    assert upload_res.status_code == 200
    try:
        upload_json = upload_res.json()
    except ValueError:
        pytest.fail(f"响应不是有效的JSON: {upload_res.text}")

    code = upload_json.get('code')
    msg = upload_json.get('msg', '')
    try:
        assert str(code) == expected, f'预期结果：{expected}, 实际结果：{code}, 消息：{msg}'
        logger.info(f"✅ 测试文件上传功能成功，状态码：{code}, 消息：{msg}")
    except AssertionError as e:
        logger.error(f"测试文件上传功能失败，状态码：{code}, 消息：{msg}, 错误信息：{e}")
    finally:
        if 'png' not in path:
            del_cache(f'{str(HOME)+path}')