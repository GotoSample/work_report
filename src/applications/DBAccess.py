"""
    DBAccess.pyは、MySQLデータベースへの接続を管理するクラスです。
"""

import pymysql
import os

class DBAccess:
    """
    DBAccessクラスは、MySQLデータベースへの接続を管理するクラスです。
    """

    def __init__(self):
        """
        __init__メソッドは、DBAccessクラスのインスタンスを初期化するメソッドです。
        MySQLデータベースへの接続を初期化します。
        MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASEは、環境変数から取得します。
        charsetは、UTF-8です。
        cursorclassは、DictCursorです。
        DictCursorは、MySQLデータベースの結果を辞書形式で取得します。
        """
        self.conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'flask_db'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_connection(self):
        """
        get_connectionメソッドは、MySQLデータベースへの接続を取得するメソッドです。
        MySQLデータベースへの接続を取得します。
        """
        return self.conn 
       
    def close_connection(self):
        """
        close_connectionメソッドは、MySQLデータベースへの接続を閉じるメソッドです。
        MySQLデータベースへの接続を閉じます。
        """
        self.conn.close()

    def execute_query(self, query, params=None):
        """
        execute_queryメソッドは、MySQLデータベースにクエリを実行するメソッドです。
        MySQLデータベースにクエリを実行します。
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
        return None
    
    def commit(self):
        """
        commitメソッドは、MySQLデータベースのトランザクションをコミットするメソッドです。
        MySQLデータベースのトランザクションをコミットします。
        """
        self.conn.commit()
        return None
    
    def get_cursor(self):
        """
        get_cursorメソッドは、MySQLデータベースのカーソルを取得するメソッドです。
        MySQLデータベースのカーソルを取得します。
        """
        return self.conn.cursor()
    
    def rollback(self):
        """
        rollbackメソッドは、MySQLデータベースのトランザクションをロールバックするメソッドです。
        MySQLデータベースのトランザクションをロールバックします。
        """
        self.conn.rollback()
        return None