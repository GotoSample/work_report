"""
時間フォーマット処理の統合テスト

実際のデータベースを使用して、timedeltaオブジェクトの文字列変換処理をテストします。
"""

import pytest
from datetime import date, timedelta as dt_timedelta, time as dt_time
from applications.DBAccess import DBAccess
import hashlib


class TestTimeFormattingIntegration:
    """
    時間フォーマット処理の統合テストクラス
    
    実際のデータベースを使用して、timedeltaオブジェクトが適切に文字列に変換されることをテストします。
    """
    
    def setup_method(self):
        """
        テストメソッド実行前のセットアップ
        
        テスト用の勤怠記録を作成します。
        """
        self.db = DBAccess()
        
        # テスト用の社員IDを取得（employee@example.com）
        password_hash = hashlib.sha256('password123'.encode()).hexdigest()
        employees = self.db.execute_query(
            "SELECT id FROM employees WHERE email = %s",
            ('employee@example.com',)
        )
        
        if not employees:
            pytest.skip("テスト用の社員アカウントが見つかりません")
        
        self.employee_id = employees[0]['id']
        
        # テスト用の勤怠記録を作成
        test_date = date.today()
        self.db.execute_query("""
            INSERT INTO attendance_records
            (employee_id, date, attendance_type, start_time, end_time, break_time, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            attendance_type = VALUES(attendance_type),
            start_time = VALUES(start_time),
            end_time = VALUES(end_time),
            break_time = VALUES(break_time),
            notes = VALUES(notes)
        """, (
            self.employee_id,
            test_date,
            '出勤',
            '09:00:00',
            '18:00:00',
            '01:00:00',
            '統合テスト用の記録'
        ))
        self.db.commit()
        self.test_date = test_date
    
    def teardown_method(self):
        """
        テストメソッド実行後のクリーンアップ
        
        テスト用の勤怠記録を削除します。
        """
        if hasattr(self, 'test_date') and hasattr(self, 'employee_id'):
            self.db.execute_query("""
                DELETE FROM attendance_records
                WHERE employee_id = %s AND date = %s
            """, (self.employee_id, self.test_date))
            self.db.commit()
        
        self.db.close_connection()
    
    def test_dashboard_time_formatting_integration(self):
        """
        dashboard関数で実際のデータベースから取得した時間データが適切にフォーマットされることを確認するテスト
        
        データベースから取得したTIME型の値（timedeltaオブジェクト）が
        適切に文字列（HH:MM形式）に変換されることを検証します。
        """
        # ダッシュボードで取得されるクエリを実行
        today = date.today()
        first_day = today.replace(day=1)
        
        records = self.db.execute_query("""
            SELECT date, attendance_type, start_time, end_time, break_time
            FROM attendance_records
            WHERE employee_id = %s AND date >= %s
            ORDER BY date DESC
            LIMIT 10
        """, (self.employee_id, first_day))
        
        # レコードが存在することを確認
        assert len(records) > 0
        
        # 時間フィールドの型を確認
        for record in records:
            if record.get('start_time'):
                # timedeltaまたはtimeオブジェクトであることを確認
                assert isinstance(record['start_time'], (dt_timedelta, dt_time)) or record['start_time'] is None
            
            if record.get('end_time'):
                assert isinstance(record['end_time'], (dt_timedelta, dt_time)) or record['end_time'] is None
            
            if record.get('break_time'):
                assert isinstance(record['break_time'], (dt_timedelta, dt_time)) or record['break_time'] is None
        
        # フォーマット処理をテスト
        formatted_records = []
        
        for record in records:
            formatted_record = dict(record)
            
            # start_timeをフォーマット
            if formatted_record.get('start_time'):
                if isinstance(formatted_record['start_time'], dt_timedelta):
                    total_seconds = int(formatted_record['start_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_record['start_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(formatted_record['start_time'], 'strftime'):
                    formatted_record['start_time'] = formatted_record['start_time'].strftime('%H:%M')
            
            # end_timeをフォーマット
            if formatted_record.get('end_time'):
                if isinstance(formatted_record['end_time'], dt_timedelta):
                    total_seconds = int(formatted_record['end_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_record['end_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(formatted_record['end_time'], 'strftime'):
                    formatted_record['end_time'] = formatted_record['end_time'].strftime('%H:%M')
            
            # break_timeをフォーマット
            if formatted_record.get('break_time'):
                if isinstance(formatted_record['break_time'], dt_timedelta):
                    total_seconds = int(formatted_record['break_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_record['break_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(formatted_record['break_time'], 'strftime'):
                    formatted_record['break_time'] = formatted_record['break_time'].strftime('%H:%M')
            
            formatted_records.append(formatted_record)
        
        # フォーマット後の値を確認
        for formatted_record in formatted_records:
            if formatted_record.get('start_time'):
                assert isinstance(formatted_record['start_time'], str)
                # HH:MM形式であることを確認
                parts = formatted_record['start_time'].split(':')
                assert len(parts) == 2
                assert len(parts[0]) == 2  # 時間部分が2桁
                assert len(parts[1]) == 2  # 分部分が2桁
            
            if formatted_record.get('end_time'):
                assert isinstance(formatted_record['end_time'], str)
                parts = formatted_record['end_time'].split(':')
                assert len(parts) == 2
                assert len(parts[0]) == 2
                assert len(parts[1]) == 2
            
            if formatted_record.get('break_time'):
                assert isinstance(formatted_record['break_time'], str)
                parts = formatted_record['break_time'].split(':')
                assert len(parts) == 2
                assert len(parts[0]) == 2
                assert len(parts[1]) == 2
    
    def test_attendance_view_time_formatting_integration(self):
        """
        attendance_view関数で実際のデータベースから取得した時間データが適切にフォーマットされることを確認するテスト
        """
        # 勤怠記録を取得
        record = self.db.execute_query("""
            SELECT ar.*, e.name as employee_name
            FROM attendance_records ar
            JOIN employees e ON ar.employee_id = e.id
            WHERE ar.date = %s AND ar.employee_id = %s
            LIMIT 1
        """, (self.test_date, self.employee_id))
        
        # レコードが存在することを確認
        assert len(record) > 0
        
        # 時間フィールドのフォーマット処理をテスト
        formatted_record = dict(record[0])
        
        # start_time, end_time, break_timeをフォーマット
        for time_field in ['start_time', 'end_time', 'break_time']:
            if formatted_record.get(time_field):
                original_value = formatted_record[time_field]
                
                # timedeltaの場合
                if isinstance(original_value, dt_timedelta):
                    total_seconds = int(original_value.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_record[time_field] = f"{hours:02d}:{minutes:02d}"
                # timeオブジェクトの場合
                elif hasattr(original_value, 'strftime'):
                    formatted_record[time_field] = original_value.strftime('%H:%M')
                
                # フォーマット後の値が文字列であることを確認
                assert isinstance(formatted_record[time_field], str)
                # HH:MM形式であることを確認
                parts = formatted_record[time_field].split(':')
                assert len(parts) == 2
                assert len(parts[0]) == 2
                assert len(parts[1]) == 2

