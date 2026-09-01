"""员工请假申请 UI 流程测试。"""
import allure
from selenium.webdriver.remote.webdriver import WebDriver
from ui_test.pages import ApproveApplyPage, ApprovalPage
from utils import Logger, DataBaseConnection
import random

@allure.epic("🖥️ UI测试")
@allure.feature("UI 申请审批全流程")
@allure.severity(allure.severity_level.BLOCKER)
class TestApprove:
    @allure.title("员工向hr发起请假申请")
    def test_staff_approve_leave(self, logged_staff_driver: WebDriver, logger: Logger) -> None:
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
            if "请选择" not in tip:
                logger.error(f"表单存在未填写的必填项: {tip}")
                allure.attach(
                    logged_staff_driver.get_screenshot_as_png(),
                    name="表单提交错误",
                    attachment_type=allure.attachment_type.PNG
                )

    @allure.title("人事经理审核请假信息")
    def test_hr_approve(self, logged_hr_driver: WebDriver, logger: Logger, db_connect: DataBaseConnection):
        """人事经理审核请假信息"""
        with allure.step("更换hr账户登录"):
            approve_page = ApprovalPage(logged_hr_driver, db_connect)
        with allure.step("进入审批中心"):
            approve_page.open_review_center()
        with allure.step("随机审核请假信息,随机拒绝通过"):
            random.choice([
                lambda: approve_page.approve(approval_step=random.randint(1, 2), comment="同意"),
                lambda: approve_page.reject(approval_step=random.randint(1, 2), comment="不同意"),
            ])()