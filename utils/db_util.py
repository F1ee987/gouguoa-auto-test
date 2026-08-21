"""
@Project:gouguoa-auto-test
@File   :db_utils.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 14:10
"""

import pymysql
from pymysql.connections import Connection
from pymysql import cursors
from typing import Optional, Any

class DataBaseConnection:
    """
    数据库连接类，用于连接MySQL数据库并执行查询操作.
    """
    def __init__(self, logger: Any) -> None:
        """
        初始化数据库连接类.
        """
        self.conn: Optional[Connection] = None
        self.logger = logger

    def get_db_connection(self, host: str, port: str|int, user: str, password: str, database: str, timeout: int = 5) -> Optional[Connection]:
        """
        连接MySQL数据库.
        :param port: 数据库端口号.
        :param host: 数据库主机地址.
        :param user: 用户名.
        :param password: 密码.
        :param database: 数据库名称.
        :param timeout: 连接超时时间，单位为秒.
        :return: MySQL数据库的连接对象.
        """
        try:
            connection: Connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=int(port),
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=timeout
            )
            self.logger.info(f"✅ 数据库连接成功")
            self.conn = connection
        except pymysql.MySQLError as e:
            self.logger.error(f"❌ 数据库连接失败，错误详情：{e}")
            return None

    def query(self, sql: str, params: Optional[tuple] = None, check_size: int = 0) -> Any:
        """
        执行SQL查询，默认返回所有结果。
        :param sql: SQL查询语句（可使用 %s 占位符）。
        :param params: 查询参数元组，用于参数化查询，防止SQL注入。
        :param check_size: 检查结果数量，大于0时只取前N条。
        :return: 查询结果列表（成功）或 None（失败）。
        """
        if self.conn:
            try:
                with self.conn.cursor() as cursor:
                    # 参数化查询：将 params 传给 execute
                    cursor.execute(sql, params)
                    if check_size > 0:
                        results = cursor.fetchmany(check_size)
                    else:
                        results = cursor.fetchall()
                    self.logger.info(f"✅ SQL查询成功，结果数量：{len(results) if results else 0}")
                    return results
            except pymysql.MySQLError as e:
                self.logger.error(f"❌ SQL查询失败：{sql[:100]}...，错误详情：{e}")
                return None
        print("❌ 数据库连接未建立或连接失败。")


    def commit(self) -> None:
        """
        提交数据库事务.
        """
        if self.conn:
            self.conn.commit()
            self.logger.info("✅ 数据库事务已提交")
        else:
            self.logger.error("❌ 数据库连接未建立或已关闭。")

    def close(self) -> None:
        """
        关闭数据库连接.
        """
        if self.conn:
            self.conn.close()
            self.logger.info(f"✅ 数据库连接已关闭")
        else:
            self.logger.error("❌ 数据库连接未建立或已关闭。")

if __name__ == "__main__":
    # 测试数据库连接
    from config.conf import DB
    from utils import Logger
    logger = Logger(__file__)
    db_conn = DataBaseConnection(logger)
    conn = db_conn.get_db_connection(**DB)
    print(db_conn.query('SELECT count(username) FROM oa_admin'))
    db_conn.close()