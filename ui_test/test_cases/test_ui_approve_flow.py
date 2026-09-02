"""员工请假申请 UI 流程测试。"""
import pytest
import allure
from selenium.webdriver.remote.webdriver import WebDriver
from ui_test.conftest import HR_ACCOUNT
from ui_test.pages import ApproveApplyPage, ApprovalPage
from utils import Logger, DataBaseConnection
import random

@allure.epic("🖥️ UI测试")
@allure.feature("UI 申请审批全流程")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ui
class TestApprove:
    @allure.title("员工向hr发起请假申请")
    def test_staff_approve_leave(self, logged_staff_driver: WebDriver, logger: Logger, db_connect: DataBaseConnection) -> None:
        """普通员工从「办公审批 -> 审批申请」发起请假申请并提交。"""
        with allure.step("员工打开办公审批页面"):
            apply_page = ApproveApplyPage(logged_staff_driver)

        with allure.step("进入审批申请并填写请假表单"):
            # 内部已覆盖：选择审批类型 -> 时间/天数/事由 -> 请假类型与流程 -> 审批人
            apply_page.fill_leave_form(
                duration="1",
                reason="自动化测试请假",
                leave_type="年假",
                department="人事部",
            )

        with allure.step("提交请假申请"):
            tip = apply_page.submit()

        with allure.step("校验提交结果"):
            print(f"提交后提示: {tip or '(无弹出层提示)'}")
            if "请选择" in tip:
                logger.error(f"表单存在未填写的必填项: {tip}")
                allure.attach(
                    logged_staff_driver.get_screenshot_as_png(),
                    name="表单提交错误",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.fail("❌ 表单提交错误")
            else:
                logger.info("✅ 提交成功")

    @allure.title("人事经理审核请假信息")
    def test_hr_approve(self, logged_hr_driver: WebDriver, logger: Logger, db_connect: DataBaseConnection):
        """人事经理审核请假信息"""
        with allure.step("更换hr账户登录"):
            # 传入 approver，只挑待当前账号审批的单子，避免打开他人待办后找不到审批按钮
            approve_page = ApprovalPage(logged_hr_driver, db_connect, approver=HR_ACCOUNT[0])
        with allure.step("进入审批中心"):
            approve_id = approve_page.open_review_center()
        with allure.step(f"随机审核id为{approve_id}请假信息,随机拒绝or通过"):
            approval_step = random.randint(1, 2)
            random.choice([
                lambda: approve_page.approve(approval_step=approval_step, comment="同意"),
                lambda: approve_page.reject(approval_step=approval_step, comment="不同意"),
            ])()
            db_connect.commit() # 提交事务
        with allure.step("校验审批结果"):
            result = db_connect.query("""
                    SELECT l.check_status, l.check_uids, a.name as next_approver_name
                    FROM oa_leaves l
                    LEFT JOIN oa_admin a ON l.check_uids = a.id
                    WHERE l.id = %s
                """,
            (approve_id,)
            )
            row = result[0]
            status = row["check_status"]
            next_approver_name = row["next_approver_name"]
            logger.info(f"审批状态: {status}" if status else "审批状态未获取到")
            if approval_step == 1: # 只审批一次
                if status == 1:
                    logger.error(f"审批状态不正确,实际状态: {status}")
                    allure.attach(
                        logged_hr_driver.get_screenshot_as_png(),
                        name="审批结果错误",
                        attachment_type=allure.attachment_type.PNG
                    )
                    pytest.fail(f"❌ 审批状态不正确,实际状态: {status}")
                else:
                    logger.info("审批通过" if status == 2 else "审批拒绝")
            else:
                if status == 2:
                    logger.info(f"当前审批通过，审批交给下级{next_approver_name}")
                else:
                    logger.info(f"当前审批拒绝，审批交给下级{next_approver_name}")