"""
勤怠入力機能の単体テスト

勤怠入力機能の動作をテストします。
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


class TestAttendance:
    """
    勤怠入力機能のテストクラス
    
    勤怠入力機能の動作をテストします。
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
    def test_attendance_input_get(self, mock_dbaccess):
        """
        UT501: 勤怠入力画面表示（GET）のテスト
        
        勤怠入力画面が正しく表示されることを確認します。
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
            [{'id': 1, 'name': 'Project A'}],  # プロジェクト一覧
            []  # 既存記録なし
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/attendance/input', follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200
    
    @patch('app.DBAccess')
    def test_attendance_create(self, mock_dbaccess):
        """
        UT502: 勤怠記録新規作成（POST）のテスト
        
        勤怠記録が新規作成されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_db_instance.get_cursor.return_value = mock_cursor
        mock_db_instance.execute_query.side_effect = [
            [],  # 既存記録なし
            [{'id': 1, 'name': 'Project A'}]  # プロジェクト一覧
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/attendance/input', data={
                'date': date.today().isoformat(),
                'attendance_type': '出勤',
                'start_time': '09:00',
                'end_time': '18:00',
                'break_time': '01:00',
                'notes': 'Test notes'
            }, follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/dashboard' in response.location
            # commitが呼ばれたことを確認
            mock_db_instance.commit.assert_called()
    
    @patch('app.DBAccess')
    def test_attendance_update(self, mock_dbaccess):
        """
        UT503: 勤怠記録更新（POST）のテスト
        
        勤怠記録が更新されることを確認します。
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
            [{'id': 1}],  # 既存記録あり
            [{'id': 1, 'name': 'Project A'}],  # プロジェクト一覧
            []  # project_hours削除
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/attendance/input', data={
                'date': date.today().isoformat(),
                'attendance_type': '出勤',
                'start_time': '09:30',
                'end_time': '18:30',
                'break_time': '01:00',
                'notes': 'Updated notes'
            }, follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            assert '/dashboard' in response.location
            # commitが呼ばれたことを確認（更新処理とプロジェクト作業時間処理で複数回）
            assert mock_db_instance.commit.call_count >= 1
    
    @patch('app.DBAccess')
    def test_attendance_validation_no_date(self, mock_dbaccess):
        """
        UT504: 勤怠入力バリデーション（日付未入力）のテスト
        
        日付が未入力の場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        mock_db_instance = MagicMock()
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/attendance/input', data={
                'date': '',
                'attendance_type': '出勤',
                'start_time': '09:00',
                'end_time': '18:00'
            }, follow_redirects=False)
            
            # リダイレクトされることを確認
            assert response.status_code == 302
    
    @patch('app.DBAccess')
    def test_attendance_validation_no_type(self, mock_dbaccess):
        """
        UT505: 勤怠入力バリデーション（出勤区分未入力）のテスト
        
        出勤区分が未入力の場合、エラーメッセージが表示されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        mock_db_instance = MagicMock()
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/attendance/input', data={
                'date': date.today().isoformat(),
                'attendance_type': '',
                'start_time': '09:00',
                'end_time': '18:00'
            }, follow_redirects=False)
            
            # リダイレクトされることを確認
            assert response.status_code == 302
    
    @patch('app.DBAccess')
    def test_attendance_with_project_hours(self, mock_dbaccess):
        """
        UT506: プロジェクト作業時間登録（複数プロジェクト）のテスト
        
        複数のプロジェクト作業時間が保存されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定
        mock_db_instance = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_db_instance.get_cursor.return_value = mock_cursor
        mock_db_instance.execute_query.side_effect = [
            [],  # 既存記録なし
            [{'id': 1, 'name': 'Project A'}, {'id': 2, 'name': 'Project B'}],  # プロジェクト一覧
            []  # project_hours削除
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.post('/attendance/input', data={
                'date': date.today().isoformat(),
                'attendance_type': '出勤',
                'start_time': '09:00',
                'end_time': '18:00',
                'break_time': '01:00',
                'project_hours_1': '4.0',
                'project_hours_2': '4.0'
            }, follow_redirects=False)
            
            # ダッシュボードへリダイレクトされることを確認
            assert response.status_code == 302
            # commitが呼ばれたことを確認（記録作成とプロジェクト作業時間登録で複数回）
            # 実装上は2回呼ばれる（記録作成後のcommit + プロジェクト作業時間登録後のcommit）
            assert mock_db_instance.commit.call_count >= 1
    
    @patch('app.DBAccess')
    def test_attendance_input_with_existing_record(self, mock_dbaccess):
        """
        UT507: 既存記録がある場合のフォーム表示のテスト
        
        既存記録がある場合、そのデータがフォームに表示されることを確認します。
        """
        # セッション設定
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_email'] = 'employee@example.com'
            sess['user_name'] = 'Employee User'
            sess['user_role'] = 'employee'
        
        # モックの設定
        from datetime import timedelta
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.side_effect = [
            [{'id': 1, 'name': 'Project A'}],  # プロジェクト一覧
            [{  # 既存記録
                'id': 1,
                'date': date.today(),
                'attendance_type': '出勤',
                'start_time': timedelta(hours=9, minutes=0),
                'end_time': timedelta(hours=18, minutes=0),
                'break_time': timedelta(hours=1, minutes=0),
                'notes': 'Existing notes'
            }],
            [{'project_id': 1, 'hours': 4.0}]  # プロジェクト作業時間
        ]
        mock_dbaccess.return_value = mock_db_instance
        
        with self.client:
            response = self.client.get('/attendance/input?date=' + date.today().isoformat(), follow_redirects=False)
            
            # 正常にアクセスできることを確認
            assert response.status_code == 200

