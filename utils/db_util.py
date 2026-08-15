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
    def __init__(self) -> None:
        """
        初始化数据库连接类.
        """
        self.conn: Optional[Connection] = None

    def get_db_connection(self, host: str, port: int, user: str, password: str, database: str, timeout: int = 5) -> Optional[Connection]:
        """
        连接MySQL数据库.
        :param port:
        :param host:
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
                port=port,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=timeout
            )
            print(f"✅ 数据库连接成功：主机>>{host}:{port}，数据库>>{database}")
            self.conn = connection
        except pymysql.MySQLError as e:
            print(f"❌ 数据库连接失败：主机>>{host}:{port}，数据库>>{database}，错误详情：{e}")
            return None

    def run_query(self, sql: str, check_size: int = 0) -> Any:
        """
        执行SQL查询,默认返回所有结果.
        :param sql: SQL查询语句.
        :param check_size: 检查结果数量.
        :return: 查询结果列表.
        """
        if self.conn:
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(sql)
                    results = cursor.fetchmany(check_size) if check_size > 0 else cursor.fetchall()
                    print(f"✅ SQL查询成功：{sql}，结果数量：{len(results) if results else 0}")
                    return results
            except pymysql.MySQLError as e:
                print(f"❌ SQL查询失败：{sql}，错误详情：{e}")
                return None
        print("❌ 数据库连接未建立或连接失败。")

    def close(self) -> None:
        """
        关闭数据库连接.
        """
        if self.conn:
            self.conn.close()
            print(f"✅ 数据库连接已关闭")
        else:
            print("❌ 数据库连接未建立或已关闭。")

if __name__ == "__main__":
    # 测试数据库连接
    from config.conf import DB
    db_conn = DataBaseConnection()
    conn = db_conn.get_db_connection(**DB)
    print(db_conn.run_query('SELECT count(username) FROM oa_admin'))
    db_conn.close()