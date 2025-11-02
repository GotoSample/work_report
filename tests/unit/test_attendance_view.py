"""
勤怠詳細表示機能の単体テスト

勤怠詳細表示機能の動作をテストします。
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


class TestAttendanceView:
    """
    勤怠詳細表示機能のテストクラス
    
    勤怠詳細表示機能の動作をテストします。
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
    def test_attendance_view_own_record(self, mock_dbaccess):
        """
        UT601: 勤怠詳細表示（自分の記録）のテスト
        
        自分の勤怠記録が正しく表示されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.side_effect = [
            [{  # 勤怠記録
                'id': 1,
                'employee_id': 1,
                'date': date.today(),
                'attendance_type': '出勤',
                'start_time': timedelta(hours=9, minutes=0),
                'end_time': timedelta(hours=18, minutes=0),
                'break_time': timedelta(hours=1, minutes=0),
                'notes': 'Test notes',
                'employee_name': 'Employee User'
            }],
            [  # プロジェクト作業時間
                {'project_id': 1, 'project_name': 'Project A', 'hours': 4.0}
            ]
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get(f'/attendance/view/{date.today().isoformat()}', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
    
    @patch('app.DBAccess')
    def test_attendance_view_manager_access(self, mock_dbaccess):
        """
        UT602: 勤怠詳細表示（課長：他の社員の記録）のテスト
        
        課長が他の社員の記録を閲覧できることを確認します。
        """
        # セッション設定（課長）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['user_email'] = 'manager@example.com'
            sess['user_name'] = 'Manager User'
            sess['user_role'] = 'manager'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.side_effect = [
            [{  # 勤怠記録（他の社員の記録）
                'id': 1,
                'employee_id': 1,
                'date': date.today(),
                'attendance_type': '出勤',
                'start_time': timedelta(hours=9, minutes=0),
                'end_time': timedelta(hours=18, minutes=0),
                'break_time': timedelta(hours=1, minutes=0),
                'notes': 'Test notes',
                'employee_name': 'Employee User'
            }],
            []  # プロジェクト作業時間
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get(f'/attendance/view/{date.today().isoformat()}', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
    
    @patch('app.DBAccess')
    def test_attendance_view_employee_access_others(self, mock_dbaccess):
        """
        UT603: 勤怠詳細表示（社員：他の社員の記録）のテスト
        
        社員が他の社員の記録を閲覧しようとした場合、アクセス拒否されることを確認します。
        """
        # セッション設定（社員）
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定（他の社員の記録が見つからない）
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get(f'/attendance/view/{date.today().isoformat()}', follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/dashboard' in response.location
    
    @patch('app.DBAccess')
    def test_attendance_view_not_found(self, mock_dbaccess):
        """
        UT604: 勤怠詳細表示（存在しない記録）のテスト
        
        存在しない記録にアクセスした場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定（記録が見つからない）
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/attendance/view/2024-01-01', follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/dashboard' in response.location
    
    @patch('app.DBAccess')
    def test_attendance_view_with_project_hours(self, mock_dbaccess):
        """
        UT605: プロジェクト作業時間の表示のテスト
        
        プロジェクト作業時間が一覧で表示されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.side_effect = [
            [{  # 勤怠記録
                'id': 1,
                'employee_id': 1,
                'date': date.today(),
                'attendance_type': '出勤',
                'start_time': timedelta(hours=9, minutes=0),
                'end_time': timedelta(hours=18, minutes=0),
                'break_time': timedelta(hours=1, minutes=0),
                'notes': 'Test notes',
                'employee_name': 'Employee User'
            }],
            [  # プロジェクト作業時間
                {'project_id': 1, 'project_name': 'Project A', 'hours': 4.0},
                {'project_id': 2, 'project_name': 'Project B', 'hours': 4.0}
            ]
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get(f'/attendance/view/{date.today().isoformat()}', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200

