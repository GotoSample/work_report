"""
勤怠管理システムのユニットテスト

勤怠管理システムの各機能のユニットテストを実装します。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, time
from applications.DBAccess import DBAccess
from applications.db_init import init_database


class TestDBAccess:
    """
    DBAccessクラスのテストクラス
    
    DBAccessクラスの各メソッドをテストします。
    """
    
    def test_execute_query(self):
        """
        execute_queryメソッドのテスト
        
        クエリが正常に実行されることを検証します。
        """
        db = DBAccess()
        try:
            # テストクエリを実行
            result = db.execute_query("SELECT 1 as test_value")
            assert result is not None
            assert len(result) > 0
            assert result[0]['test_value'] == 1
        finally:
            db.close_connection()
    
    def test_commit(self):
        """
        commitメソッドのテスト
        
        トランザクションが正常にコミットされることを検証します。
        """
        db = DBAccess()
        try:
            # コミットが正常に実行されることを確認（エラーが発生しない）
            db.commit()
            assert True
        finally:
            db.close_connection()
    
    def test_rollback(self):
        """
        rollbackメソッドのテスト
        
        トランザクションが正常にロールバックされることを検証します。
        """
        db = DBAccess()
        try:
            # ロールバックが正常に実行されることを確認（エラーが発生しない）
            db.rollback()
            assert True
        finally:
            db.close_connection()


class TestDatabaseInitialization:
    """
    データベース初期化のテストクラス
    
    データベースの初期化機能をテストします。
    """
    
    def test_init_database(self):
        """
        init_database関数のテスト
        
        データベースが正常に初期化されることを検証します。
        """
        try:
            init_database()
            
            # テーブルが作成されていることを確認
            db = DBAccess()
            tables = db.execute_query("SHOW TABLES")
            
            # キー名を確認（MySQLのバージョンによって異なる可能性がある）
            if tables:
                first_key = list(tables[0].keys())[0]
                table_names = [t[first_key] for t in tables]
            else:
                table_names = []
            
            assert 'employees' in table_names
            assert 'attendance_records' in table_names
            assert 'projects' in table_names
            assert 'project_hours' in table_names
            
            # 初期データが投入されていることを確認
            employees = db.execute_query("SELECT * FROM employees")
            assert len(employees) >= 2  # 最低2つのテストアカウントがあることを確認
            
            projects = db.execute_query("SELECT * FROM projects")
            assert len(projects) >= 1  # 最低1つのプロジェクトがあることを確認
            
            db.close_connection()
        except Exception as e:
            pytest.fail(f"データベース初期化エラー: {str(e)}")


class TestAuthentication:
    """
    認証機能のテストクラス
    
    ログイン機能をテストします。
    """
    
    def test_employee_login(self):
        """
        社員ログインのテスト
        
        社員アカウントでログインできることを検証します。
        """
        db = DBAccess()
        try:
            import hashlib
            password_hash = hashlib.sha256('password123'.encode()).hexdigest()
            
            # 社員アカウントが存在することを確認
            employees = db.execute_query(
                "SELECT * FROM employees WHERE email = %s AND password = %s",
                ('employee@example.com', password_hash)
            )
            
            assert len(employees) > 0
            assert employees[0]['email'] == 'employee@example.com'
            assert employees[0]['role'] == 'employee'
            
            db.close_connection()
        except Exception as e:
            pytest.fail(f"認証テストエラー: {str(e)}")
    
    def test_manager_login(self):
        """
        課長ログインのテスト
        
        課長アカウントでログインできることを検証します。
        """
        db = DBAccess()
        try:
            import hashlib
            password_hash = hashlib.sha256('password123'.encode()).hexdigest()
            
            # 課長アカウントが存在することを確認
            managers = db.execute_query(
                "SELECT * FROM employees WHERE email = %s AND password = %s",
                ('manager@example.com', password_hash)
            )
            
            assert len(managers) > 0
            assert managers[0]['email'] == 'manager@example.com'
            assert managers[0]['role'] == 'manager'
            
            db.close_connection()
        except Exception as e:
            pytest.fail(f"認証テストエラー: {str(e)}")

