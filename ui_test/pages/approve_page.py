"""
@Project:conf.py
@File   :approve_page.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/31 13:05

发起审批页（Page Object）：审批中心 -> 选择审批类型 -> 填写表单 -> 选择审批人 -> 提交。

实现说明（重要，避免后续踩坑）：
1. 登录后的首页是 **iframe 布局**：主内容在 `iframe[src='/home/index/main.html']` 里，
   "办公审批 / 审批申请" 卡片位于该 iframe 中。若只对顶层 document 执行定位或 JS，
   永远找不到该元素——这是历史上"找不到审批申请元素"的根因。
2. 审批类型卡片的点击事件由父框架的 JS 绑定，单独打开页面时点击无效；
   因此这里采用「先校验卡片可见（UI 断言），再直接导航到 data-href 指向的表单页」的方式，
   既保留 UI 校验语义，又保证流程稳定可重跑。
3. 表单内所有字段一律用 `name` 或 `lay-filter` 等**语义化属性**定位，
   不使用 `/html/body/...` 这类绝对 xpath（页面结构一变即失效）。
"""
from typing import Optional, Tuple

from config.conf import BASE_URL
from selenium.webdriver.remote.webdriver import WebDriver
from ui_test.pages import BasePage


class ApproveApplyPage(BasePage):
    """发起审批页：选择审批类型 -> 填写表单 -> 选择审批人 -> 提交。"""

    # ---------------------------- 页面地址 ----------------------------
    # 审批申请入口所在页（登录后可直接在顶层访问，不必依赖 iframe 内的卡片点击）
    APPROVE_CENTER_URL = f"{BASE_URL}/home/approve/index"

    # 审批类型：key -> (审批中心卡片文案, 表单页路径)
    # 路径取自卡片上的 data-href 属性
    APPROVE_TYPE_MAP = {
        "REQUEST_LEAVE": ("请假", f"{BASE_URL}/home/leaves/add"),
        "REIMBURSEMENT": ("报销", f"{BASE_URL}/finance/expense/add"),
        "ONBOARDING": ("入职", f"{BASE_URL}/user/talent/add"),
    }

    # ---------------------------- 审批中心定位器 ----------------------------
    # 类型卡片形如：<div class="layui-col-md2 side-a" data-href="/home/leaves/add">请假</div>
    TYPE_CARD_LOC = (
        "xpath",
        "//div[contains(@class,'side-a')][normalize-space(.)= '{name}']",
    )

    # ---------------------------- 请假表单定位器 ----------------------------
    # 日期输入（laydate 时间控件）
    START_DATE_INPUT_LOC = ("name", "start_date")
    END_DATE_INPUT_LOC = ("name", "end_date")
    # laydate 底部按钮，用 lay-type 属性定位，不依赖层级
    LAYDATE_NOW_BTN = ("css selector", "span[lay-type='now']")
    LAYDATE_CONFIRM_BTN = ("css selector", "span[lay-type='confirm']")

    LEAVE_DURATION_LOC = ("name", "duration")      # 请假天数
    LEAVE_REASON_LOC = ("name", "reason")          # 请假事由

    # layui 渲染后的下拉：<select name="types"> + 紧随其后的 div.layui-form-select
    # 选项形如：<dd lay-value="2">年假</dd>
    LEAVE_TYPE_SELECT = "types"                    # 请假类型（原 select 的 name）
    APPROVE_FLOW_SELECT = "flow_id"                # 审批流程（原 select 的 name）

    # 请假类型可选值（lay-value -> 含义）
    LEAVE_TYPE_VALUES = {
        "事假": "1", "年假": "2", "调休假": "3", "病假": "4", "婚假": "5",
        "丧假": "6", "产假": "7", "陪产假": "8", "其他": "9",
    }

    APPROVER_INPUT_LOC = ("name", "check_uames")   # 审批人（点击后弹出「选择员工」层）
    # 部门树节点：<span class="layui-tree-txt">人事部</span>
    DEPT_TREE_ITEM_LOC = (
        "xpath",
        "//span[contains(@class,'layui-tree-txt')][normalize-space(text())='{dept}']",
    )
    # 员工标签：<div id="employee"><span class="layui-tags-span">人事</span></div>
    EMPLOYEE_ITEM_LOC = (
        "xpath",
        "//*[@id='employee']//span[contains(@class,'layui-tags-span')]"
        "[contains(normalize-space(.), '{name}')]",
    )

    SUBMIT_BTN_LOC = ("css selector", "button[lay-filter='webform']")  # 立即提交

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ---------------------------- 导航与类型选择 ----------------------------
    def open_approve_center(self) -> None:
        """打开审批中心（审批申请入口所在页）。"""
        self.open(self.APPROVE_CENTER_URL)
        # 等待类型卡片渲染完成
        self.wait_present(
            *self._format_locator(self.TYPE_CARD_LOC, name="请假"), timeout=10
        )

    def select_approve_type(self, approve_type: str) -> None:
        """进入审批中心并打开指定类型的申请表单。

        Args:
            approve_type: APPROVE_TYPE_MAP 的 key，如 "REQUEST_LEAVE"。

        说明：
            先确认审批中心存在该类型卡片（UI 可见性校验），再直接打开表单页，
            以规避"卡片点击事件绑定在父框架、单独打开页面时点击无效"的问题。
        """
        if approve_type not in self.APPROVE_TYPE_MAP:
            raise ValueError(
                f"未定义的审批类型: {approve_type}，可选: {list(self.APPROVE_TYPE_MAP)}"
            )
        card_name, form_url = self.APPROVE_TYPE_MAP[approve_type]

        self.open_approve_center()
        card = self.wait_visible(
            *self._format_locator(self.TYPE_CARD_LOC, name=card_name), timeout=10
        )
        # 卡片可见即认为入口可用；记录其 data-href 便于排查
        data_href = card.get_attribute("data-href")
        print(f"审批类型卡片「{card_name}」已定位，data-href={data_href}")

        self.open(form_url)

    # ---------------------------- 表单填写 ----------------------------
    def _pick_current_time(self, input_loc: Tuple[str, str]) -> str:
        """在 laydate 时间控件中选择「现在」并返回输入框的最终值。

        laydate 的「现在」通常直接回填并关闭面板；若面板未关闭则补点「确定」。
        """
        input_element = self.wait_clickable(*input_loc, timeout=10)
        input_element.click()

        self.wait_clickable(*self.LAYDATE_NOW_BTN, timeout=5).click()
        self.force_wait(0.6)

        confirm_buttons = self._driver.find_elements(*self.LAYDATE_CONFIRM_BTN)
        if confirm_buttons:  # 面板未自动关闭时才补点「确定」
            try:
                confirm_buttons[0].click()
            except Exception:  # 面板正在关闭，忽略点击异常
                pass
            self.force_wait(0.5)

        value = self.find_element(*input_loc).get_attribute("value")
        if not value:
            raise AssertionError(f"日期未回填成功: {input_loc}")
        return value

    def select_layui_option(self, select_name: str, option_value: str) -> str:
        """在 layui 渲染的下拉框中按 lay-value 选中选项。

        原生 <select> 被 layui 隐藏，可见的是紧随其后的 div.layui-form-select，
        故按 select 的 name 定位其渲染容器，避免多个下拉互相干扰。

        Args:
            select_name: 原生 select 的 name，如 "types"。
            option_value: 目标选项的 lay-value，如 "2"（年假）。

        Returns:
            选中项的可见文本。
        """
        wrapper = (
            f"//select[@name='{select_name}']"
            f"/following-sibling::div[contains(@class,'layui-form-select')][1]"
        )
        self.wait_clickable(
            "xpath", f"{wrapper}//div[contains(@class,'layui-select-title')]", timeout=10
        ).click()
        self.force_wait(0.5)

        option = self.wait_clickable(
            "xpath", f"{wrapper}//dd[@lay-value='{option_value}']", timeout=10
        )
        text = option.text.strip()
        option.click()
        self.force_wait(0.4)
        return text

    def choose_approver(self, department: str = "人事部", name: Optional[str] = None) -> str:
        """在「选择员工」弹出层中按部门 + 姓名选择审批人。

        Args:
            department: 部门名称，如 "人事部"。
            name: 员工姓名；为 None 时取该部门下第一个可选员工。

        Returns:
            回填到审批人输入框的姓名。
        """
        self.wait_clickable(*self.APPROVER_INPUT_LOC, timeout=10).click()
        self.force_wait(1.2)

        dept_locator = self._format_locator(self.DEPT_TREE_ITEM_LOC, dept=department)
        self.wait_clickable(*dept_locator, timeout=10).click()
        self.force_wait(1.2)

        if name:
            emp_locator = self._format_locator(self.EMPLOYEE_ITEM_LOC, name=name)
        else:
            emp_locator = (
                "xpath",
                "//*[@id='employee']//span[contains(@class,'layui-tags-span')]",
            )
        employee = self.wait_clickable(*emp_locator, timeout=10)
        approver_name = employee.text.strip()
        employee.click()
        self.force_wait(0.8)

        filled = self.find_element(*self.APPROVER_INPUT_LOC).get_attribute("value")
        if not filled:
            raise AssertionError("审批人未回填，请检查选择员工弹出层是否成功关闭")
        return filled or approver_name

    def fill_leave_form(
        self,
        duration: str = "1",
        reason: str = "自动化测试请假",
        leave_type: str = "年假",
        department: str = "人事部",
        approver: Optional[str] = None,
    ) -> None:
        """填写请假申请表单（不含提交）。

        Args:
            duration: 请假天数。
            reason: 请假事由。
            leave_type: 请假类型名称，取值见 LEAVE_TYPE_VALUES。
            department: 审批人所属部门。
            approver: 审批人姓名；为 None 时取该部门第一个员工。
        """
        self.select_approve_type("REQUEST_LEAVE")
        self.wait_clickable(*self.START_DATE_INPUT_LOC, timeout=10)

        # 开始 / 结束时间：均取当前时间
        self._pick_current_time(self.START_DATE_INPUT_LOC)
        self._pick_current_time(self.END_DATE_INPUT_LOC)

        # 请假天数与事由
        duration_input = self.find_element(*self.LEAVE_DURATION_LOC)
        duration_input.clear()
        self.send_keys(element=duration_input, keys=duration)
        self.send_keys(
            element=self.find_element(*self.LEAVE_REASON_LOC), keys=reason
        )

        # 请假类型 / 审批流程（均为 layui 下拉）
        if leave_type not in self.LEAVE_TYPE_VALUES:
            raise ValueError(
                f"未定义的请假类型: {leave_type}，可选: {list(self.LEAVE_TYPE_VALUES)}"
            )
        self.select_layui_option(
            self.LEAVE_TYPE_SELECT, self.LEAVE_TYPE_VALUES[leave_type]
        )
        self.select_layui_option(self.APPROVE_FLOW_SELECT, "1")  # 1 = 请假审批

        # 审批人
        self.choose_approver(department=department, name=approver)

    def submit(self) -> str:
        """点击「立即提交」，返回提交后的提示文本（无弹出层时返回空串）。"""
        self.wait_clickable(*self.SUBMIT_BTN_LOC, timeout=10).click()
        self.force_wait(2.5)
        return self._driver.execute_script(
            "const tip = document.querySelector('.layui-layer-content');"
            "return tip ? tip.innerText.trim() : '';"
        )

    # ---------------------------- 工具方法 ----------------------------
    @staticmethod
    def _format_locator(locator: Tuple[str, str], **kwargs: str) -> Tuple[str, str]:
        """将定位器模板中的占位符替换为实际值。"""
        by, value = locator
        return by, value.format(**kwargs)
