"""
@Project:gouguoa-auto-test
@File   :test_approval_flow.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/19 15:56
"""
from config.conf import SUBMIT_CHECK, APPROVE_URL
from datetime import datetime
from random import choice
from typing import Dict, Any

class TestLeaveApprovalFlow:
    """请假审批全流程"""
    start_time = '2026-07-'+str(choice(range(1,30)))+" 09:00"
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    submit_data: Dict[str, Any] = {
        "types": 1,
        "start_date": start_time,
        "end_date": end_time,
        "reason": "临时有事",
        "duration": 7,
        "id": 0,
        "flow_id": 1,
        "action_id": 1,
        "check_uames": "超级员工",
        "check_uids": 1,
        "check_name": "leaves"
    }

    approve_data = {
        'action_id': '1',
        'check_name': 'leaves',
        'check_flow_id': '1',
        'check_node': '1',
        'check_uids': '',
        'check': '1',
        'check_files': '',
        'content': '通过'
    }

    header = {
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    def test_staff_apply(self, normal_api_login: Any, logger: Any):
        """员工申请"""
        resp = normal_api_login.post(SUBMIT_CHECK,data=self.submit_data)

        assert resp.status_code == 200, logger.error(f"员工提交请假申请失败，响应状态码: {resp.status_code}")
        assert resp.json().get('code') == 0, logger.error(f"员工提交请假申请失败，响应内容: {resp.json()}")
        logger.info(f"✅ 员工提交请假申请成功")

    def test_manager_approve(self, admin_api_login: Any, logger: Any):
        """经理审批"""
        resp = admin_api_login.post(APPROVE_URL,data=self.approve_data,headers=self.header)
        assert resp.status_code == 200, logger.error(f"经理审批请假申请失败，响应状态码: {resp.status_code}")
        assert resp.json().get('code') == 0, logger.error(f"经理审批请假申请失败，响应内容: {resp.json()}")
        logger.info(f"✅ 经理审批请假申请成功")