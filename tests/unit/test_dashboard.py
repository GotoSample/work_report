"""
ダッシュボード機能の単体テスト

ダッシュボード機能の動作をテストします。
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import date, timedelta

# コンテナ内のパス構造に対応するため、パスを追加
sys.path.insert(0, '/usr/src/app')
# ローカル環境用のフォールバック
if not os.path.exists('/usr/src/app/app.py'):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from app import app


class TestDashboard:
    """
    ダッシュボード機能のテストクラス
    
    ダッシュボード機能の動作をテストします。
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
    def test_dashboard_with_login(self, mock_dbaccess):
        """
        UT401: ダッシュボード表示（ログイン済み）のテスト
        
        ログイン済み状態でダッシュボードにアクセスした場合、今月の勤怠記録が表示されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [
            {
                'date': date.today(),
                'attendance_type': '出勤',
                'start_time': timedelta(hours=9, minutes=0),
                'end_time': timedelta(hours=18, minutes=0),
                'break_time': timedelta(hours=1, minutes=0)
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/dashboard', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
            # データが取得されたことを確認
            mock_db_instance.execute_query.assert_called_once()
    
    def test_dashboard_without_login(self):
        """
        UT402: ダッシュボード表示（未ログイン）のテスト
        
        未ログイン状態でダッシュボードにアクセスした場合、ログインページへリダイレクトされることを確認します。
        """
        with self.client:
            response = self.client.get('/dashboard', follow_redirects=False)
            
            # ログインページへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/login' in response.location
    
    @patch('app.DBAccess')
    def test_dashboard_no_records(self, mock_dbaccess):
        """
        UT403: ダッシュボード表示（記録なし）のテスト
        
        勤怠記録がない場合、空のリストが表示されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定（空のリスト）
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/dashboard', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
            # データベースクエリが実行されたことを確認
            mock_db_instance.execute_query.assert_called_once()

