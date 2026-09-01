"""员工请假申请 UI 流程测试。"""
import allure
from selenium.webdriver.remote.webdriver import WebDriver
from ui_test.pages import ApproveApplyPage
from utils import Logger


@allure.epic("🖥️ UI测试")
@allure.feature("UI 申请审批全流程")
@allure.severity(allure.severity_level.BLOCKER)
class TestApprove:
    @allure.title("员工向hr发起请假申请")
    def test_staff_approve_leave(self,logged_in_driver: WebDriver, logger: Logger) -> None:
        """普通员工从「办公审批 -> 审批申请」发起请假申请并提交。"""
        approve_page = ApproveApplyPage(logged_in_driver)

        with allure.step("进入审批申请并填写请假表单"):
            # 内部已覆盖：选择审批类型 -> 时间/天数/事由 -> 请假类型与流程 -> 审批人
            approve_page.fill_leave_form(
                duration="1",
                reason="自动化测试请假",
                leave_type="年假",
                department="人事部",
            )

        with allure.step("提交请假申请"):
            tip = approve_page.submit()

        with allure.step("校验提交结果"):
            print(f"提交后提示: {tip or '(无弹出层提示)'}")
            if "请选择" not in tip:
                logger.error(f"表单存在未填写的必填项: {tip}")
                allure.attach(
                    logged_in_driver.get_screenshot_as_png(),
                    name="表单提交错误",
                    attachment_type=allure.attachment_type.PNG
                )

    @allure.title("人事经理审核请假信息")
    def test_hr_approve(self):
        """人事经理审核请假信息"""
        with allure.step("更换hr账户登录"):

