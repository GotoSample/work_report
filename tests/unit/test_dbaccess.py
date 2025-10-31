"""
DBAccess.pyの単体テスト

DBAccessクラスの各メソッドの動作をテストします。
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
import os
import pymysql

# コンテナ内のパス構造に対応するため、パスを追加
sys.path.insert(0, '/usr/src/app')
# ローカル環境用のフォールバック
if not os.path.exists('/usr/src/app/applications/DBAccess.py'):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from applications.DBAccess import DBAccess


class TestDBAccess:
    """
    DBAccessクラスのテストクラス
    
    各メソッドの動作をテストします。
    """
    
    @patch('applications.DBAccess.pymysql.connect')
    def test_init(self, mock_connect):
        """
        __init__メソッドのテスト
        
        インスタンス作成時にMySQLデータベースへの接続が正しく初期化されることを確認します。
        """
        # モックの設定
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # インスタンス作成
        db = DBAccess()
        
        # 接続が呼ばれたことを確認
        mock_connect.assert_called_once_with(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'flask_db'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # 接続オブジェクトが保存されていることを確認
        assert db.conn == mock_conn
    
    @patch('applications.DBAccess.pymysql.connect')
    def test_get_connection(self, mock_connect):
        """
        get_connectionメソッドのテスト
        
        接続オブジェクトが正しく返されることを確認します。
        """
        # モックの設定
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # インスタンス作成
        db = DBAccess()
        
        # get_connection()を呼び出し
        result = db.get_connection()
        
        # 接続オブジェクトが返されることを確認
        assert result == mock_conn
    
    @patch('applications.DBAccess.pymysql.connect')
    def test_close_connection(self, mock_connect):
        """
        close_connectionメソッドのテスト
        
        接続が正しく閉じられることを確認します。
        """
        # モックの設定
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # インスタンス作成
        db = DBAccess()
        
        # close_connection()を呼び出し
        db.close_connection()
        
        # 接続のclose()が呼ばれたことを確認
        mock_conn.close.assert_called_once()
    
    @patch('applications.DBAccess.pymysql.connect')
    def test_execute_query_success(self, mock_connect):
        """
        execute_queryメソッドの正常系テスト
        
        クエリが正しく実行され、結果が返されることを確認します。
        """
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn
        
        # クエリ結果の設定
        expected_results = [{'id': 1, 'name': 'test'}]
        mock_cursor.fetchall.return_value = expected_results
        
        # インスタンス作成
        db = DBAccess()
        
        # execute_query()を呼び出し
        query = "SELECT * FROM test_table"
        results = db.execute_query(query)
        
        # カーソルが作成されたことを確認
        mock_conn.cursor.assert_called()
        # クエリが実行されたことを確認
        mock_cursor.execute.assert_called_once_with(query, None)
        # fetchall()が呼ばれたことを確認
        mock_cursor.fetchall.assert_called_once()
        # 結果が正しく返されることを確認
        assert results == expected_results
    
    @patch('applications.DBAccess.pymysql.connect')
    def test_execute_query_with_params(self, mock_connect):
        """
        execute_queryメソッドのパラメータ付きクエリのテスト
        
        パラメータ付きクエリが正しく実行されることを確認します。
        """
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn
        
        # クエリ結果の設定
        expected_results = [{'id': 1}]
        mock_cursor.fetchall.return_value = expected_results
        
        # インスタンス作成
        db = DBAccess()
        
        # execute_query()をパラメータ付きで呼び出し
        query = "SELECT * FROM test_table WHERE id = %s"
        params = (1,)
        results = db.execute_query(query, params)
        
        # パラメータ付きでクエリが実行されたことを確認
        mock_cursor.execute.assert_called_once_with(query, params)
        # 結果が正しく返されることを確認
        assert results == expected_results
    
    @patch('applications.DBAccess.pymysql.connect')
    def test_commit(self, mock_connect):
        """
        commitメソッドのテスト
        
        トランザクションが正しくコミットされることを確認します。
        """
        # モックの設定
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # インスタンス作成
        db = DBAccess()
        
        # commit()を呼び出し
        result = db.commit()
        
        # 接続のcommit()が呼ばれたことを確認
        mock_conn.commit.assert_called_once()
        # Noneが返されることを確認
        assert result is None
    
    @patch('applications.DBAccess.pymysql.connect')
    def test_get_cursor(self, mock_connect):
        """
        get_cursorメソッドのテスト
        
        カーソルが正しく取得されることを確認します。
        """
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # インスタンス作成
        db = DBAccess()
        
        # get_cursor()を呼び出し
        result = db.get_cursor()
        
        # カーソルが作成されたことを確認
        mock_conn.cursor.assert_called_once()
        # カーソルが返されることを確認
        assert result == mock_cursor
    
    @patch('applications.DBAccess.pymysql.connect')
    def test_rollback(self, mock_connect):
        """
        rollbackメソッドのテスト
        
        トランザクションが正しくロールバックされることを確認します。
        """
        # モックの設定
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # インスタンス作成
        db = DBAccess()
        
        # rollback()を呼び出し
        result = db.rollback()
        
        # 接続のrollback()が呼ばれたことを確認
        mock_conn.rollback.assert_called_once()
        # Noneが返されることを確認
        assert result is None

