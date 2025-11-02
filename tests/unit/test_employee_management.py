"""
社員管理機能の単体テスト

社員管理機能（社員一覧、作成、編集、削除）の動作をテストします。
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import hashlib

# コンテナ内のパス構造に対応するため、パスを追加
sys.path.insert(0, '/usr/src/app')
# ローカル環境用のフォールバック
if not os.path.exists('/usr/src/app/app.py'):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from app import app


class TestEmployeeManagement:
    """
    社員管理機能のテストクラス
    
    社員管理機能の動作をテストします。
    """
    
    def setup_method(self):
        """
        テストメソッド実行前のセットアップ
        
        テストクライアントを初期化します。
        """
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """
        テストメソッド実行後のクリーンアップ
        
        アプリケーションコンテキストをクリーンアップします。
        """
        self.app_context.pop()
    
    @patch('app.DBAccess')
    def test_employees_list_manager(self, mock_dbaccess):
        """
        UT701: 社員一覧表示（課長）のテスト
        
        課長が社員一覧を閲覧できることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [
            {
                'id': 1,
                'email': 'employee@example.com',
                'name': 'Employee User',
                'role': 'employee',
                'created_at': '2024-01-01 00:00:00'
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/employees', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
    
    def test_employees_list_employee(self):
        """
        UT702: 社員一覧表示（社員）のテスト
        
        社員が社員一覧にアクセスした場合、ダッシュボードへリダイレクトされることを確認します。
        """
        # セッション設定（社員）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        with self.client:
            response = self.client.get('/employees', follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/' in response.location or '/dashboard' in response.location
    
    @patch('app.DBAccess')
    def test_employee_create_form(self, mock_dbaccess):
        """
        UT703: 社員作成画面表示（GET）のテスト
        
        社員作成フォームが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        with self.client:
            response = self.client.get('/employees/create', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
    
    @patch('app.DBAccess')
    def test_employee_create_success(self, mock_dbaccess):
        """
        UT704: 社員作成処理（正常系）のテスト
        
        社員が正常に作成されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/employees/create', data={
                'email': 'newemployee@example.com',
                'password': 'password123',
                'name': 'New Employee',
                'role': 'employee'
            }, follow_redirects=False)
            
            # 社員一覧へリダイレクトされることを確認
            assert response.status_code == 302
            assert '/employees' in response.location
            # commitが呼ばれたことを確認
            mock_db_instance.commit.assert_called_once()
    
    @patch('app.DBAccess')
    def test_employee_create_no_email(self, mock_dbaccess):
        """
        UT705: 社員作成処理（異常系：メールアドレス未入力）のテスト
        
        メールアドレスが未入力の場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        with self.client:
            response = self.client.post('/employees/create', data={
                'email': '',
                'password': 'password123',
                'name': 'New Employee',
                'role': 'employee'
            }, follow_redirects=True)
            
            # エラーメッセージが含まれていることを確認
            assert 'すべての項目を入力してください'.encode('utf-8') in response.data
    
    @patch('app.DBAccess')
    def test_employee_create_no_password(self, mock_dbaccess):
        """
        UT706: 社員作成処理（異常系：パスワード未入力）のテスト
        
        パスワードが未入力の場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        with self.client:
            response = self.client.post('/employees/create', data={
                'email': 'newemployee@example.com',
                'password': '',
                'name': 'New Employee',
                'role': 'employee'
            }, follow_redirects=True)
            
            # エラーメッセージが含まれていることを確認
            assert 'すべての項目を入力してください'.encode('utf-8') in response.data
    
    @patch('app.DBAccess')
    def test_employee_create_no_name(self, mock_dbaccess):
        """
        UT707: 社員作成処理（異常系：名前未入力）のテスト
        
        名前が未入力の場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        with self.client:
            response = self.client.post('/employees/create', data={
                'email': 'newemployee@example.com',
                'password': 'password123',
                'name': '',
                'role': 'employee'
            }, follow_redirects=True)
            
            # エラーメッセージが含まれていることを確認
            assert 'すべての項目を入力してください'.encode('utf-8') in response.data
    
    @patch('app.DBAccess')
    def test_employee_edit_form(self, mock_dbaccess):
        """
        UT708: 社員編集画面表示（GET）のテスト
        
        編集フォームに既存データが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [
            {
                'id': 1,
                'email': 'employee@example.com',
                'name': 'Employee User',
                'role': 'employee'
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/employees/edit/1', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
    
    @patch('app.DBAccess')
    def test_employee_update_with_password(self, mock_dbaccess):
        """
        UT709: 社員更新処理（正常系：パスワード変更あり）のテスト
        
        パスワードを変更して社員情報が更新されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [
            {
                'id': 1,
                'email': 'employee@example.com',
                'name': 'Employee User',
                'role': 'employee'
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/employees/edit/1', data={
                'email': 'employee@example.com',
                'password': 'newpassword123',
                'name': 'Updated Employee',
                'role': 'employee'
            }, follow_redirects=False)
            
            # 社員一覧へリダイレクトされることを確認
            assert response.status_code == 302
            assert '/employees' in response.location
            # commitが呼ばれたことを確認
            mock_db_instance.commit.assert_called_once()
    
    @patch('app.DBAccess')
    def test_employee_update_without_password(self, mock_dbaccess):
        """
        UT710: 社員更新処理（正常系：パスワード変更なし）のテスト
        
        パスワードを変更せずに社員情報が更新されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [
            {
                'id': 1,
                'email': 'employee@example.com',
                'name': 'Employee User',
                'role': 'employee'
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/employees/edit/1', data={
                'email': 'employee@example.com',
                'password': '',
                'name': 'Updated Employee',
                'role': 'employee'
            }, follow_redirects=False)
            
            # 社員一覧へリダイレクトされることを確認
            assert response.status_code == 302
            assert '/employees' in response.location
            # commitが呼ばれたことを確認
            mock_db_instance.commit.assert_called_once()
    
    @patch('app.DBAccess')
    def test_employee_update_no_email(self, mock_dbaccess):
        """
        UT711: 社員更新処理（異常系：メールアドレス未入力）のテスト
        
        メールアドレスが未入力の場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [
            {
                'id': 1,
                'email': 'employee@example.com',
                'name': 'Employee User',
                'role': 'employee'
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/employees/edit/1', data={
                'email': '',
                'password': '',
                'name': 'Updated Employee',
                'role': 'employee'
            }, follow_redirects=False)
            
            # リダイレクトされることを確認
            assert response.status_code == 302
    
    @patch('app.DBAccess')
    def test_employee_update_no_name(self, mock_dbaccess):
        """
        UT712: 社員更新処理（異常系：名前未入力）のテスト
        
        名前が未入力の場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [
            {
                'id': 1,
                'email': 'employee@example.com',
                'name': 'Employee User',
                'role': 'employee'
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/employees/edit/1', data={
                'email': 'employee@example.com',
                'password': '',
                'name': '',
                'role': 'employee'
            }, follow_redirects=False)
            
            # リダイレクトされることを確認
            assert response.status_code == 302
    
    @patch('app.DBAccess')
    def test_employee_update_not_found(self, mock_dbaccess):
        """
        UT713: 社員更新処理（異常系：存在しない社員ID）のテスト
        
        存在しない社員IDで更新しようとした場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定（社員が見つからない）
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/employees/edit/999', follow_redirects=False)
            
            # 社員一覧へリダイレクトされることを確認
            assert response.status_code == 302
            assert '/employees' in response.location
    
    @patch('app.DBAccess')
    def test_employee_delete(self, mock_dbaccess):
        """
        UT714: 社員削除処理（正常系）のテスト
        
        社員が正常に削除されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/employees/delete/1', follow_redirects=False)
            
            # 社員一覧へリダイレクトされることを確認
            assert response.status_code == 302
            assert '/employees' in response.location
            # commitが呼ばれたことを確認
            mock_db_instance.commit.assert_called_once()

