"""
数据库工具：封装 MySQL 连接与查询。

说明：
- 连接信息来自 config.conf 的 DB 字典；
- 所有查询均使用参数化（%s 占位符）以防范 SQL 注入；
- 连接失败或查询失败时记录日志并返回 None，由调用方决定如何处理。
"""
import pymysql
from pymysql.connections import Connection
from typing import Any, Optional, Tuple

from utils.logger import Logger


class DataBaseConnection:
    """MySQL 数据库连接封装，支持连接、查询、提交与关闭。"""

    def __init__(self, logger: Logger) -> None:
        self.conn: Optional[Connection] = None
        self.logger = logger

    def connect(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        timeout: float = 5,
    ) -> Optional[Connection]:
        """建立数据库连接，成功后将连接对象保存在 self.conn。

        Args:
            host: 数据库主机地址。
            port: 数据库端口号。
            user: 用户名。
            password: 密码。
            database: 数据库名。
            timeout: 连接超时时间（秒），默认 5。
        Returns:
            成功返回连接对象，失败返回 None。
        """
        try:
            connection: Connection = pymysql.connect(
                host=host,
                user=str(user),
                password=str(password),
                database=database,
                port=int(port),
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=timeout,
            )
            self.conn = connection
            self.logger.info("✅ 数据库连接成功")
            return connection
        except pymysql.MySQLError as e:
            self.logger.error(f"❌ 数据库连接失败，错误详情：{e}")
            return None
        except ValueError as ve:
            self.logger.error(f"❌ 数据库连接参数错误，错误详情：{ve}")
            return None

    def query(
        self,
        sql: str,
        params: Optional[Tuple[Any, ...]] = None,
        limit: int = 0,
    ) -> Any:
        """执行 SQL 查询，默认返回全部结果。

        Args:
            sql: SQL 查询语句（使用 %s 占位符）。
            params: 查询参数元组，用于参数化查询。
            limit: 大于 0 时只取前 N 条（fetchmany）。
        Returns:
            查询结果列表（成功）或 None（失败 / 未连接）。
        """
        if not self.conn:
            self.logger.error("❌ 数据库连接未建立或已关闭，无法执行查询。")
            return None
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchmany(limit) if limit > 0 else cursor.fetchall()
                self.logger.info(f"✅ SQL 查询成功，结果数量：{len(results) if results else 0}")
                return results
        except pymysql.MySQLError as e:
            self.logger.error(f"❌ SQL 查询失败：{sql[:100]}...，错误详情：{e}")
            return None

    def commit(self) -> None:
        """提交数据库事务。"""
        if self.conn:
            self.conn.commit()
            self.logger.info("✅ 数据库事务已提交")
        else:
            self.logger.error("❌ 数据库连接未建立或已关闭，无法提交。")

    def close(self) -> None:
        """关闭数据库连接。"""
        if self.conn:
            self.conn.close()
            self.logger.info("✅ 数据库连接已关闭")
        else:
            self.logger.error("❌ 数据库连接未建立或已关闭。")


if __name__ == "__main__":
    from config.conf import DB
    from utils import Logger

    logger = Logger(__file__)
    db = DataBaseConnection(logger)
    db.connect(**DB)
    print(db.query('SELECT count(username) FROM oa_admin'))
    db.close()
