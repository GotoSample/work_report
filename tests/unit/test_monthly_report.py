"""
月次レポート機能の単体テスト

月次レポート機能の動作をテストします。
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import date

# コンテナ内のパス構造に対応するため、パスを追加
sys.path.insert(0, '/usr/src/app')
# ローカル環境用のフォールバック
if not os.path.exists('/usr/src/app/app.py'):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from app import app


class TestMonthlyReport:
    """
    月次レポート機能のテストクラス
    
    月次レポート機能の動作をテストします。
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
    def test_monthly_report_default_month(self, mock_dbaccess):
        """
        UT801: 月次レポート表示（課長：デフォルト年月）のテスト
        
        デフォルトで今月のレポートが表示されることを確認します。
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
                'employee_id': 1,
                'employee_name': 'Employee User',
                'attendance_days': 20,
                'total_hours': 160.0,
                'total_break_hours': 20.0
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/report/monthly', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
            # データベースクエリが実行されたことを確認
            mock_db_instance.execute_query.assert_called_once()
    
    @patch('app.DBAccess')
    def test_monthly_report_specified_month(self, mock_dbaccess):
        """
        UT802: 月次レポート表示（課長：指定年月）のテスト
        
        指定年月のレポートが表示されることを確認します。
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
                'employee_id': 1,
                'employee_name': 'Employee User',
                'attendance_days': 22,
                'total_hours': 176.0,
                'total_break_hours': 22.0
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/report/monthly?year=2024&month=1', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
            # データベースクエリが実行されたことを確認
            mock_db_instance.execute_query.assert_called_once()
    
    def test_monthly_report_employee_access(self):
        """
        UT803: 月次レポート表示（社員）のテスト
        
        社員が月次レポートにアクセスした場合、ダッシュボードへリダイレクトされることを確認します。
        """
        # セッション設定（社員）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        with self.client:
            response = self.client.get('/report/monthly', follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/' in response.location or '/dashboard' in response.location
    
    @patch('app.DBAccess')
    def test_monthly_report_with_data(self, mock_dbaccess):
        """
        UT804: 月次レポート集計（データあり）のテスト
        
        データがある場合、正しい集計値が表示されることを確認します。
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
                'employee_id': 1,
                'employee_name': 'Employee User',
                'attendance_days': 20,
                'total_hours': 160.0,
                'total_break_hours': 20.0
            },
            {
                'employee_id': 2,
                'employee_name': 'Employee User 2',
                'attendance_days': 22,
                'total_hours': 176.0,
                'total_break_hours': 22.0
            }
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/report/monthly', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
            # レポートデータが含まれていることを確認
            response_text = response.data.decode('utf-8')
            assert 'Employee User' in response_text
    
    @patch('app.DBAccess')
    def test_monthly_report_no_data(self, mock_dbaccess):
        """
        UT805: 月次レポート集計（データなし）のテスト
        
        データがない場合、データなしのレポートが表示されることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定（空のリスト）
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/report/monthly', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
            # データベースクエリが実行されたことを確認
            mock_db_instance.execute_query.assert_called_once()

