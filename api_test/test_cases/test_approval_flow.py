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
        "types": 2,                 # 请假类型：1=事假，2=病假，3=年假……
        "start_date": start_time,   # 请假开始时间，格式 "YYYY-MM-DD HH:mm:ss"
        "end_date": end_time,       # 请假结束时间，格式同上
        "reason": "临时有事",        # 请假原因
        "duration": 1,              # 请假时长（单位：天）
        "id": 0,                    # 请假单ID：0 表示新建，非0 表示编辑已有单据
        "flow_id": 1,               # 审批流ID：标识使用哪一套审批流程（如部门经理→人事→总经理）
        "action_id": 1,             # 当前节点动作ID：通常与 flow_id 关联，1 表示“提交申请”
        "check_uames": "人事",       # 下一级审批人姓名（字符串，多个用逗号分隔）
        "check_uids": 3,            # 下一级审批人用户ID（整数，多个用逗号分隔的字符串）
        "check_name": "leaves"      # 审批表单名称，固定值 "leaves"（请假审批表）
    }

    approve_data = {
        'action_id': '1',       # 当前操作的动作ID，与提交时的 action_id 一致
        'check_name': 'leaves', # 审批表单名称，固定值 "leaves"
        'check_flow_id': '1',   # 审批流ID，与提交时的 flow_id 对应
        'check_node': '1',      # 当前审批节点序号：1=第一个节点（经理审批）
        'check_uids': '',       # 下一级审批人ID列表：空字符串表示审批结束（无后续节点）
        # 若有下一级，格式如 "2,3"
        'check': '1',           # 审批结果：'1'=同意（通过），'2'=驳回，'3'=撤销
        'check_files': '',      # 附件文件路径：空字符串表示无附件
        'content': '测试审核意见'       # 审批意见文字
    }

    header = {
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    def test_staff_apply(self, normal_api_login: Any, logger: Any):
        """员工向人事提交请假申请"""
        resp = normal_api_login.post(SUBMIT_CHECK,data=self.submit_data)

        assert resp.status_code == 200, logger.error(f"员工提交请假申请失败，响应状态码: {resp.status_code}")
        assert resp.json().get('code') == 0, logger.error(f"员工提交请假申请失败，响应内容: {resp.json()}")
        logger.info(f"✅ 员工提交请假申请成功, msg:{resp.json().get('msg')}")

    def test_manager_approve(self, admin_api_login: Any, logger: Any):
        """总经理无审批权限，不审批"""
        resp = admin_api_login.post(APPROVE_URL,data=self.approve_data,headers=self.header)
        assert resp.status_code == 200, logger.error("连接服务器失败")
        assert resp.json().get('code') == 1, logger.error(f"总经理审核预期code为1，实际为{resp.json().get('code')}")
        logger.info(f"✅ 总经理无审批权限，审批失败, msg:{resp.json().get('msg')}")

    def test_hr_approve(self, hr_api_login: Any, logger: Any):
        """人事经理有审批权限，审批"""
        resp = hr_api_login.post(APPROVE_URL,data=self.approve_data,headers=self.header)
        assert resp.status_code == 200, logger.error("连接服务器失败")
        assert resp.json().get('code') == 0, logger.error("人事经理审批失败")
        logger.info(f"✅ 人事经理审批通过, msg:{resp.json().get('msg')}")