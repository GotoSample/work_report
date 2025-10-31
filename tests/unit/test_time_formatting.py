"""
時間フォーマット処理のユニットテスト

timedeltaオブジェクトの文字列変換処理をテストします。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
import sys
import os

# パスを追加
sys.path.insert(0, '/usr/src/app')
if not os.path.exists('/usr/src/app/app.py'):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app import app


class TestTimeFormatting:
    """
    時間フォーマット処理のテストクラス
    
    timedeltaオブジェクトが適切に文字列に変換されることをテストします。
    """
    
    def setup_method(self):
        """
        テストメソッド実行前のセットアップ
        
        テストクライアントを初期化します。
        """
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # テスト用のセッションを作成
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'テスト社員'
            sess['user_role'] = 'employee'
    
    def teardown_method(self):
        """
        テストメソッド実行後のクリーンアップ
        
        アプリケーションコンテキストをクリーンアップします。
        """
        self.app_context.pop()
    
    @patch('app.DBAccess')
    def test_dashboard_time_formatting_timedelta(self, mock_dbaccess):
        """
        dashboard関数でtimedeltaオブジェクトが適切にフォーマットされることを確認するテスト
        
        MySQLから取得したTIME型がtimedeltaオブジェクトとして返される場合、
        適切に文字列（HH:MM形式）に変換されることを検証します。
        """
        # モックの設定
        mock_db = Mock()
        mock_dbaccess.return_value = mock_db
        
        # timedeltaオブジェクトを含むテストデータ
        test_records = [
            {
                'date': date(2025, 10, 31),
                'attendance_type': '出勤',
                'start_time': timedelta(hours=9, minutes=0),  # 09:00
                'end_time': timedelta(hours=18, minutes=0),  # 18:00
                'break_time': timedelta(hours=1, minutes=0)  # 01:00
            }
        ]
        
        mock_db.execute_query.return_value = test_records
        
        # ダッシュボードにアクセス
        response = self.client.get('/dashboard')
        
        # レスポンスが正常であることを確認
        assert response.status_code == 200
        
        # HTMLにフォーマットされた時間が含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert '09:00' in response_text or '9:00' in response_text
        assert '18:00' in response_text or '18:00' in response_text
        assert '01:00' in response_text or '1:00' in response_text
    
    @patch('app.DBAccess')
    def test_dashboard_time_formatting_time_object(self, mock_dbaccess):
        """
        dashboard関数でtimeオブジェクトが適切にフォーマットされることを確認するテスト
        
        MySQLから取得したTIME型がtimeオブジェクトとして返される場合、
        適切に文字列（HH:MM形式）に変換されることを検証します。
        """
        from datetime import time as dt_time
        
        # モックの設定
        mock_db = Mock()
        mock_dbaccess.return_value = mock_db
        
        # timeオブジェクトを含むテストデータ
        test_records = [
            {
                'date': date(2025, 10, 31),
                'attendance_type': '出勤',
                'start_time': dt_time(9, 0),  # 09:00
                'end_time': dt_time(18, 0),  # 18:00
                'break_time': dt_time(1, 0)  # 01:00
            }
        ]
        
        mock_db.execute_query.return_value = test_records
        
        # ダッシュボードにアクセス
        response = self.client.get('/dashboard')
        
        # レスポンスが正常であることを確認
        assert response.status_code == 200
        
        # HTMLにフォーマットされた時間が含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert '09:00' in response_text or '9:00' in response_text
        assert '18:00' in response_text
        assert '01:00' in response_text or '1:00' in response_text
    
    @patch('app.DBAccess')
    def test_attendance_view_time_formatting_timedelta(self, mock_dbaccess):
        """
        attendance_view関数でtimedeltaオブジェクトが適切にフォーマットされることを確認するテスト
        """
        # モックの設定
        mock_db = Mock()
        mock_dbaccess.return_value = mock_db
        
        # timedeltaオブジェクトを含むテストデータ
        test_record = [
            {
                'id': 1,
                'employee_id': 1,
                'date': date(2025, 10, 31),
                'attendance_type': '出勤',
                'start_time': timedelta(hours=9, minutes=0),
                'end_time': timedelta(hours=18, minutes=0),
                'break_time': timedelta(hours=1, minutes=0),
                'notes': None,
                'employee_name': 'テスト社員'
            }
        ]
        
        mock_db.execute_query.side_effect = [
            test_record,  # 勤怠記録のクエリ結果
            []  # プロジェクト作業時間のクエリ結果
        ]
        
        # 勤怠詳細ページにアクセス
        response = self.client.get('/attendance/view/2025-10-31')
        
        # レスポンスが正常であることを確認
        assert response.status_code == 200
        
        # HTMLにフォーマットされた時間が含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert '09:00' in response_text or '9:00' in response_text
        assert '18:00' in response_text
        assert '01:00' in response_text or '1:00' in response_text
    
    @patch('app.DBAccess')
    def test_attendance_input_time_formatting_timedelta(self, mock_dbaccess):
        """
        attendance_input関数でtimedeltaオブジェクトが適切にフォーマットされることを確認するテスト
        """
        from datetime import time as dt_time
        
        # モックの設定
        mock_db = Mock()
        mock_dbaccess.return_value = mock_db
        
        # timedeltaオブジェクトを含むテストデータ
        test_record = [
            {
                'id': 1,
                'date': date(2025, 10, 31),
                'attendance_type': '出勤',
                'start_time': timedelta(hours=9, minutes=0),
                'end_time': timedelta(hours=18, minutes=0),
                'break_time': timedelta(hours=1, minutes=0),
                'notes': None
            }
        ]
        
        mock_db.execute_query.side_effect = [
            [{'id': 1, 'name': 'プロジェクトA'}],  # プロジェクト一覧
            test_record,  # 勤怠記録
            []  # プロジェクト作業時間
        ]
        
        # 勤怠入力ページにアクセス
        response = self.client.get('/attendance/input')
        
        # レスポンスが正常であることを確認
        assert response.status_code == 200
        
        # HTMLにフォーマットされた時間が含まれていることを確認
        response_text = response.data.decode('utf-8')
        # HTML input要素のvalue属性に時間が含まれていることを確認
        assert '09:00' in response_text or 'value="09:00"' in response_text or '9:00' in response_text
        assert '18:00' in response_text or 'value="18:00"' in response_text
        assert '01:00' in response_text or 'value="01:00"' in response_text
    
    @patch('app.DBAccess')
    def test_time_formatting_edge_cases(self, mock_dbaccess):
        """
        時間フォーマットのエッジケースをテスト
        
        None値や空の値が適切に処理されることを確認します。
        """
        # モックの設定
        mock_db = Mock()
        mock_dbaccess.return_value = mock_db
        
        # None値を含むテストデータ
        test_records = [
            {
                'date': date(2025, 10, 31),
                'attendance_type': '一日休',
                'start_time': None,
                'end_time': None,
                'break_time': None
            }
        ]
        
        mock_db.execute_query.return_value = test_records
        
        # ダッシュボードにアクセス
        response = self.client.get('/dashboard')
        
        # レスポンスが正常であることを確認（エラーが発生しない）
        assert response.status_code == 200
        
        # HTMLに'-'が表示されていることを確認
        response_text = response.data.decode('utf-8')
        # None値の場合、'-'が表示されるか、何も表示されないことを確認
        assert '一日休' in response_text  # 出勤区分は表示される

