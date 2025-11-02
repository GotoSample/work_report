"""
認証・認可デコレータの単体テスト

login_requiredとmanager_requiredデコレータの動作をテストします。
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# コンテナ内のパス構造に対応するため、パスを追加
sys.path.insert(0, '/usr/src/app')
# ローカル環境用のフォールバック
if not os.path.exists('/usr/src/app/app.py'):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from app import app, login_required, manager_required
from flask import session


class TestAuthDecorators:
    """
    認証・認可デコレータのテストクラス
    
    デコレータの動作をテストします。
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
    
    def test_login_required_without_session(self):
        """
        UT301: 認証デコレータ（未ログイン）のテスト
        
        未ログイン状態でアクセスした場合、ログインページへリダイレクトされることを確認します。
        """
        with self.client:
            # セッションなしでダッシュボードにアクセス
            response = self.client.get('/dashboard', follow_redirects=False)
            
            # ログインページへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/login' in response.location
    
    def test_login_required_with_session(self):
        """
        UT302: 認証デコレータ（ログイン済み）のテスト
        
        ログイン済み状態でアクセスした場合、正常にアクセスできることを確認します。
        """
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'test@example.com'
            sess['user_name'] = 'Test User'
            sess['user_role'] = 'employee'
        
        with patch('app.DBAccess') as mock_dbaccess:
            mock_db_instance = MagicMock()
            mock_db_instance.execute_query.return_value = []
            mock_dbaccess.return_value = mock_db_instance
            
            response = self.client.get('/dashboard', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
            mock_dbaccess.assert_called_once()
    
    def test_manager_required_with_employee_role(self):
        """
        UT303: 権限チェックデコレータ（社員権限でアクセス）のテスト
        
        社員権限で課長専用機能にアクセスした場合、ダッシュボードへリダイレクトされることを確認します。
        """
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee'
            sess['user_role'] = 'employee'
        
        response = self.client.get('/employees', follow_redirects=False)
        
        # ダッシュボードへリダイレクトされることを確認
        assert response.status_code == 302
        assert '/' in response.location or '/dashboard' in response.location
    
    def test_manager_required_with_manager_role(self):
        """
        UT304: 権限チェックデコレータ（課長権限でアクセス）のテスト
        
        課長権限で課長専用機能にアクセスした場合、正常にアクセスできることを確認します。
        """
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager'
            sess['user_role'] = 'manager'
        
        with patch('app.DBAccess') as mock_dbaccess:
            mock_db_instance = MagicMock()
            mock_db_instance.execute_query.return_value = []
            mock_dbaccess.return_value = mock_db_instance
            
            response = self.client.get('/employees', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
            mock_dbaccess.assert_called_once()
    
    def test_manager_required_without_session(self):
        """
        UT305: 権限チェックデコレータ（未ログインでアクセス）のテスト
        
        未ログイン状態で課長専用機能にアクセスした場合、ログインページへリダイレクトされることを確認します。
        """
        with self.client:
            response = self.client.get('/employees', follow_redirects=False)
            
            # ログインページへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/login' in response.location

