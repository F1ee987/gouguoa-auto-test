"""
请假审批全流程接口测试。

流程节点：
    1) 员工提交请假申请（normal_api_login，期望成功 code=0）；
    2) 总经理节点无审批权限（本用例以管理员会话模拟该节点，期望 code=1）；
    3) 人事经理审批（hr_api_login，期望成功 code=0）。
"""
from datetime import datetime
from random import choice
from typing import Any, Dict

from config.conf import APPROVE_URL, SUBMIT_CHECK
from utils import Logger, RequestHandle
from api_test.helpers.response import assert_api_success


class TestLeaveApprovalFlow:
    """请假审批全流程。"""

    # 提交请假申请的数据模板（字段含义见行内注释）
    SUBMIT_DATA: Dict[str, Any] = {
        "types": 2,                     # 请假类型：1=事假，2=病假，3=年假……
        "start_date": f"2026-07-{choice(range(1, 30))} 09:00",
        "end_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "reason": "临时有事",            # 请假原因
        "duration": 1,                  # 请假时长（天）
        "id": 0,                        # 请假单 ID：0=新建，非 0=编辑
        "flow_id": 1,                   # 审批流 ID
        "action_id": 1,                 # 当前节点动作：1=提交申请
        "check_uames": "人事",           # 下一级审批人姓名
        "check_uids": 3,                # 下一级审批人用户 ID
        "check_name": "leaves",         # 审批表单名称（固定值）
    }

    # 审批动作的数据模板
    APPROVE_DATA = {
        "action_id": "1",       # 动作 ID，与提交时一致
        "check_name": "leaves", # 审批表单名称
        "check_flow_id": "1",   # 审批流 ID
        "check_node": "1",      # 当前审批节点序号（1=经理节点）
        "check_uids": "",       # 下一级审批人 ID（空=审批结束）
        "check": "1",           # 审批结果：1=同意，2=驳回，3=撤销
        "check_files": "",      # 附件路径
        "content": "测试审核意见",  # 审批意见
    }

    REQUEST_HEADERS = {
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }

    def test_staff_apply(self, normal_api_login: RequestHandle, logger: Logger):
        """员工向人事提交请假申请，期望成功（code=0）。"""
        response = normal_api_login.post(SUBMIT_CHECK, data=self.SUBMIT_DATA)
        body = assert_api_success(response, context="员工提交请假申请")
        logger.info(f"✅ 员工提交请假申请成功, msg:{body.get('msg')}")

    def test_manager_approve(self, admin_api_login: RequestHandle, logger: Logger):
        """以管理员会话模拟总经理节点审批，该节点无审批权限，期望 code=1。"""
        response = admin_api_login.post(
            APPROVE_URL, data=self.APPROVE_DATA, headers=self.REQUEST_HEADERS
        )
        body = assert_api_success(response, expected_code=1, context="总经理节点审批")
        logger.info(f"✅ 总经理无审批权限，审批失败, msg:{body.get('msg')}")

    def test_hr_approve(self, hr_api_login: RequestHandle, logger: Logger):
        """人事经理具有审批权限，期望 code=0。"""
        response = hr_api_login.post(
            APPROVE_URL, data=self.APPROVE_DATA, headers=self.REQUEST_HEADERS
        )
        body = assert_api_success(response, context="人事经理审批")
        logger.info(f"✅ 人事经理审批通过, msg:{body.get('msg')}")
