"""
@Project:conf.py
@File   :approval_page.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/9/1 11:58
"""
import pytest
from ui_test.pages import BasePage
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from config.conf import BASE_URL
from utils import DataBaseConnection
from typing import Optional
from enum import IntEnum

class LeaveStatus(IntEnum):
    """请假状态枚举"""
    PENDING = 1   # 待审批
    APPROVED = 2  # 已通过
    REJECTED = 3  # 已驳回

class ApprovalPage(BasePage):
    """经理审批页面"""
    _FINISH_NEXT_XPATH = '//*[@id="checkBox"]/form/table/tbody/tr[5]/td[2]/div[{action}]'
    APPROVE_COMMENT_INPUT = ("xpath", '//*[@id="checkBox"]/form/table/tbody/tr[7]/td[2]/textarea') # 审批意见输入框
    CHECK_UNAME = ("xpath", '//*[@id="checkBox"]/form/table/tbody/tr[5]/td[2]/div[3]/input[1]')#下一个审批人选择框
    NEXT_APPROVER_DEPT = ("xpath", '//*[@id="employeeDepament"]/div/div/div[2]/div[3]/div/div/span[2]') #下一个审批人部门
    NEXT_APPROVER_NAME = ("xpath", '//*[@id="employee"]/span') #下一个审批人姓名
    _BT_XPATH = '//*[@id="checkBox"]/form/div/span[{action}]'
    # layui 确认弹层：层 id 形如 layui-layerN，N 随本次会话累计打开的层数递增，
    # 因此不能写死下标，只能按「可见 + z-index 最大」取当前弹出的那层。
    _DIALOG_CSS = "div.layui-layer.layui-layer-dialog"
    _DIALOG_CONFIRM_BTN_CSS = ".layui-layer-btn0"  # 确定
    _DIALOG_CANCEL_BTN_CSS = ".layui-layer-btn1"  # 取消


    #---------------------------- 定位器 -----------------
    def _bt_locator(self, action: str) -> tuple:
        """生成审批按钮定位器"""
        return "xpath", self._BT_XPATH.format(action=action)

    def _finish_or_next_locator(self, action: str) -> tuple:
        """
        :param action: "finish" | "next"
        """
        index = 1 if action == "finish" else 2
        return "xpath", self._FINISH_NEXT_XPATH.format(action=index)

    def __init__(
        self,
        driver: WebDriver,
        db: Optional[DataBaseConnection] = None,
        approver: Optional[str] = None,
    ):
        """
        Args:
            driver: 浏览器驱动。
            db: 数据库连接对象。
            approver: 当前登录账号（oa_admin.username）。传入后只挑待其审批的记录，
                      不传则退化为「任意一条待审批记录」。
        """
        super().__init__(driver)
        if not db:
            raise ValueError("数据库连接对象不能为空")
        self.db = db
        self.approver = approver
        self._approver_uid = self._fetch_admin_uid(approver) if approver else None

    def _fetch_admin_uid(self, username: str) -> Optional[int]:
        """按登录账号查询 admin 主键，用于筛选待其审批的记录。"""
        rows = self.db.query("SELECT id FROM oa_admin WHERE username = %s", (username,))
        return rows[0]["id"] if rows else None

    def _fetch_pending_id(self) -> Optional[int]:
        """查询一条待审批的请假记录 ID。

        仅按 check_status 过滤会挑到「别人待审批」的单子，打开后页面没有审批按钮
        必然超时，因此指定了 approver 时追加 check_uids 过滤（check_uids 以逗号
        分隔存多个审批人，用 FIND_IN_SET 精确匹配其中一项）。
        """
        sql = "SELECT id FROM oa_leaves WHERE check_status = %s"
        params: list = [LeaveStatus.PENDING]
        if self._approver_uid:
            sql += " AND FIND_IN_SET(%s, check_uids)"
            params.append(str(self._approver_uid))
        sql += " ORDER BY id DESC LIMIT 1"

        rows = self.db.query(sql, tuple(params))
        # 按你的 db 封装调整取值方式：dict 用 rows[0]["id"]，tuple 用 rows[0][0]
        return rows[0]["id"] if rows else None

    @staticmethod
    def _review_url(approve_id: int) -> str:
        """返回指定请假记录的审批页面 URL"""
        return f"{BASE_URL}/home/leaves/view?id={approve_id}"

    #---------------------------- 操作 --------------------------
    def open_review_center(self, approve_id: Optional[int] = None) -> int:
        """打开审批详情页；不传 id 则自动取一条待审批记录，返回实际使用的 ID"""
        approve_id = approve_id or self._fetch_pending_id()
        if not approve_id:
            pytest.skip("没有待审批的请假记录")
        print("打开审批详情页，实际使用的请假记录 ID:", approve_id)
        self.open(self._review_url(approve_id))
        return approve_id    # 返回给调用方做后续断言

    def _next_approver(self, approval_step: int = 1) -> None:
        """
        是否继续审批，审批结束或审批通过并转交下一审批人
        :param approval_step: 审批步骤（1：审批结束；2：审批通过并转交下一审批人）
        :return: None
        """
        if approval_step == 1:
            self.wait_clickable(*self._finish_or_next_locator('finish')).click()
        elif approval_step == 2:
            self.wait_clickable(*self._finish_or_next_locator('next')).click()
            self.wait_clickable(*self.CHECK_UNAME).click()
            self.wait_clickable(*self.NEXT_APPROVER_DEPT).click()
            self.wait_clickable(*self.NEXT_APPROVER_NAME).click()
        else:
            raise ValueError("无效的审批步骤")

    #---------------------------- layui 确认弹层 --------------------------
    def _top_dialog_id(self, timeout: float = 5) -> str:
        """返回当前最上层可见确认弹层的 id。

        层 id（layui-layerN）由 layui 动态分配，多次弹层叠加时序号不固定，
        统一按 z-index 取最上层，避免定位串层。
        """
        self.wait_visible("css selector", self._DIALOG_CSS, timeout)
        # 弹层是 position: fixed，offsetParent 恒为 null，必须靠渲染盒子判断可见性
        layer_id = self._driver.execute_script(
            "const layers = [...document.querySelectorAll(arguments[0])].filter(el => {"
            "  const cs = getComputedStyle(el);"
            "  if (cs.display === 'none' || cs.visibility === 'hidden') return false;"
            "  return el.getClientRects().length > 0;"
            "});"
            "if (!layers.length) return '';"
            "layers.sort((a, b) => (parseInt(getComputedStyle(b).zIndex) || 0)"
            "  - (parseInt(getComputedStyle(a).zIndex) || 0));"
            "return layers[0].id;",
            self._DIALOG_CSS,
        )
        if not layer_id:
            raise NoSuchElementException(f"未找到可见的确认弹层: {self._DIALOG_CSS}")
        return layer_id

    def _click_dialog_button(self, button_css: str, timeout: float = 5) -> None:
        """点击当前确认弹层中的指定按钮（确定 / 取消）。"""
        layer_id = self._top_dialog_id(timeout)
        self.wait_clickable("css selector", f"#{layer_id} {button_css}", timeout).click()

    def _wait_dialog_closed(self, timeout: float = 5) -> None:
        """等待确认弹层关闭，为提交请求留出处理时间；超时不抛错。"""
        try:
            WebDriverWait(self._driver, timeout).until_not(
                EC.visibility_of_element_located(("css selector", self._DIALOG_CSS))
            )
        except TimeoutException:
            pass

    def approve(self, approval_step: int = 1, comment: str = "同意"):
        """
        审批通过请假申请

        :param approval_step: 审批步骤（1：审批结束；2：审批通过并转交下一审批人）
        :param comment: 审批意见，允许为空字符串
        :return: None
        """
        self._next_approver(approval_step)
        self.send_keys(*self.APPROVE_COMMENT_INPUT, keys=comment)
        self.wait_clickable(*self._bt_locator('1')).click()
        self._click_dialog_button(self._DIALOG_CONFIRM_BTN_CSS)  # 弹层「确定」
        self._wait_dialog_closed()

    def reject(self, approval_step: int = 1, comment: str = "不同意"):
        """
        拒绝请假申请
        :param approval_step: 审批步骤（1：审批结束；2：审批通过并转交下一审批人）
        :param comment: 审批意见，允许为空字符串
        :return: None
        """
        self._next_approver(approval_step)
        self.send_keys(*self.APPROVE_COMMENT_INPUT, keys=comment)
        self.wait_clickable(*self._bt_locator('2')).click()
        self._click_dialog_button(self._DIALOG_CONFIRM_BTN_CSS)  # 弹层「确定」
        self._wait_dialog_closed()