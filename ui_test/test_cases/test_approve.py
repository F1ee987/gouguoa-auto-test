from ui_test.pages import ApproveApplyPage
from selenium.webdriver.remote.webdriver import WebDriver

def test_staff_approve_leave(logged_in_driver: WebDriver) -> None:
    approve_page = ApproveApplyPage(logged_in_driver)
    approve_page.fill_leave_form()