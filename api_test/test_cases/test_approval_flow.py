"""
@Project:gouguoa-auto-test
@File   :test_approval_flow.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/19 15:56
"""
from config.conf import SUBMIT_CHECK
from datetime import datetime
from random import choice

class TestLeaveApprovalFlow:
    """请假审批全流程"""
    start_time = '2026-07-'+str(choice(range(1,30)))+" 09:00"
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    submit_data = {
        "types": 1,
        "start_date": start_time,
        "end_date": end_time,
        "reason": "临时有事",
        "duration": 7,
        "id": 0,
        "flow_id": 1,
        "action_id": 1,
        "check_uames": "赵启",
        "check_uids": 22,
        "check_name": "leaves"
    }

    def test_staff_apply(self, normal_api_login):
        """员工申请"""
        normal_api_login.post(SUBMIT_CHECK,data=self.submit_data)

    def test_manager_approve(self, admin_api_login):
        """经理审批"""
        admin_api_login.post(SUBMIT_CHECK)