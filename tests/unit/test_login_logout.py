"""
ログイン・ログアウト機能の単体テスト

ログイン・ログアウト機能の動作をテストします。
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


class TestLoginLogout:
    """
    ログイン・ログアウト機能のテストクラス
    
    ログイン・ログアウト機能の動作をテストします。
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
    def test_login_success_employee(self, mock_dbaccess):
        """
        UT201: ログイン処理（正常系：社員）のテスト
        
        社員アカウントでログインが成功することを確認します。
        """
        # モックの設定
        password_hash = hashlib.sha256('password123'.encode()).hexdigest()
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
            response = self.client.post('/login', data={
                'email': 'employee@example.com',
                'password': 'password123'
            }, follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/dashboard' in response.location
            
            # セッションが作成されていることを確認
            with self.client.session_transaction() as sess:
                assert sess['user_id'] == 1
                assert sess['user_email'] == 'employee@example.com'
                assert sess['user_name'] == 'Employee User'
                assert sess['user_role'] == 'employee'
    
    @patch('app.DBAccess')
    def test_login_success_manager(self, mock_dbaccess):
        """
        UT202: ログイン処理（正常系：課長）のテスト
        
        課長アカウントでログインが成功することを確認します。
        """
        # モックの設定
        password_hash = hashlib.sha256('password123'.encode()).hexdigest()
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [
            {
                'id': 2,
                'email': 'manager@example.com',
                'name': 'Manager User',
                'role': 'manager'
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/login', data={
                'email': 'manager@example.com',
                'password': 'password123'
            }, follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/dashboard' in response.location
            
            # セッションが作成されていることを確認
            with self.client.session_transaction() as sess:
                assert sess['user_id'] == 2
                assert sess['user_email'] == 'manager@example.com'
                assert sess['user_name'] == 'Manager User'
                assert sess['user_role'] == 'manager'
    
    @patch('app.DBAccess')
    def test_login_failure_wrong_password(self, mock_dbaccess):
        """
        UT203: ログイン処理（異常系：パスワード不一致）のテスト
        
        パスワードが間違っている場合、ログインが失敗することを確認します。
        """
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []  # ユーザーが見つからない
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/login', data={
                'email': 'employee@example.com',
                'password': 'wrongpassword'
            }, follow_redirects=True)
            
            # ログイン画面に留まることを確認
            assert response.status_code == 200
            # エラーメッセージが含まれていることを確認
            assert 'メールアドレスまたはパスワードが正しくありません'.encode('utf-8') in response.data
    
    @patch('app.DBAccess')
    def test_login_failure_no_email(self, mock_dbaccess):
        """
        UT204: ログイン処理（異常系：メールアドレス未入力）のテスト
        
        メールアドレスが未入力の場合、ログインが失敗することを確認します。
        """
        with self.client:
            response = self.client.post('/login', data={
                'email': '',
                'password': 'password123'
            }, follow_redirects=True)
            
            # ログイン画面に留まることを確認
            assert response.status_code == 200
            # エラーメッセージが含まれていることを確認
            assert 'メールアドレスとパスワードを入力してください'.encode('utf-8') in response.data
    
    @patch('app.DBAccess')
    def test_login_failure_no_password(self, mock_dbaccess):
        """
        UT205: ログイン処理（異常系：パスワード未入力）のテスト
        
        パスワードが未入力の場合、ログインが失敗することを確認します。
        """
        with self.client:
            response = self.client.post('/login', data={
                'email': 'employee@example.com',
                'password': ''
            }, follow_redirects=True)
            
            # ログイン画面に留まることを確認
            assert response.status_code == 200
            # エラーメッセージが含まれていることを確認
            assert 'メールアドレスとパスワードを入力してください'.encode('utf-8') in response.data
    
    @patch('app.DBAccess')
    def test_login_failure_no_email_no_password(self, mock_dbaccess):
        """
        UT206: ログイン処理（異常系：メールアドレス・パスワード未入力）のテスト
        
        メールアドレスとパスワードが未入力の場合、ログインが失敗することを確認します。
        """
        with self.client:
            response = self.client.post('/login', data={
                'email': '',
                'password': ''
            }, follow_redirects=True)
            
            # ログイン画面に留まることを確認
            assert response.status_code == 200
            # エラーメッセージが含まれていることを確認
            assert 'メールアドレスとパスワードを入力してください'.encode('utf-8') in response.data
    
    @patch('app.DBAccess')
    def test_login_failure_user_not_found(self, mock_dbaccess):
        """
        UT207: ログイン処理（異常系：存在しないユーザー）のテスト
        
        存在しないユーザーの場合、ログインが失敗することを確認します。
        """
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []  # ユーザーが見つからない
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/login', data={
                'email': 'nonexistent@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            # ログイン画面に留まることを確認
            assert response.status_code == 200
            # エラーメッセージが含まれていることを確認
            assert 'メールアドレスまたはパスワードが正しくありません'.encode('utf-8') in response.data
    
    def test_logout(self):
        """
        UT208: ログアウト処理のテスト
        
        ログアウトが正常に動作し、セッションがクリアされることを確認します。
        """
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'test@example.com'
            sess['user_name'] = 'Test User'
            sess['user_role'] = 'employee'
        
        with self.client:
            response = self.client.get('/logout', follow_redirects=False)
            
            # ログインページへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/login' in response.location
            
            # セッションがクリアされていることを確認
            with self.client.session_transaction() as sess:
                assert 'user_id' not in sess

