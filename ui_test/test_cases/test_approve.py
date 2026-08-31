"""员工请假申请 UI 流程测试。"""
import allure
from selenium.webdriver.remote.webdriver import WebDriver
from ui_test.pages import ApproveApplyPage


@allure.epic("🖥️ UI测试")
@allure.feature("UI 申请审批全流程")
@allure.title("员工请假申请")
def test_staff_approve_leave(logged_in_driver: WebDriver) -> None:
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
        assert "请选择" not in tip, f"表单存在未填写的必填项: {tip}"
