"""
データベース初期化スクリプト

データベースのテーブルを作成し、初期データを投入します。
"""

from applications.DBAccess import DBAccess
import hashlib
from datetime import datetime


def init_database():
    """
    データベースを初期化するメソッド
    
    必要なテーブルを作成し、初期データを投入します。
    """
    db = DBAccess()
    
    try:
        # 社員テーブルの作成
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(100) NOT NULL,
                role ENUM('employee', 'manager') DEFAULT 'employee',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # プロジェクトテーブルの作成
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 勤怠記録テーブルの作成
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id INT NOT NULL,
                date DATE NOT NULL,
                attendance_type ENUM('出勤', '遅刻', '早退', '午前休', '午後休', '一日休') DEFAULT '出勤',
                start_time TIME,
                end_time TIME,
                break_time TIME DEFAULT '01:00:00',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                UNIQUE KEY unique_employee_date (employee_id, date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # プロジェクト作業時間テーブルの作成
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS project_hours (
                id INT AUTO_INCREMENT PRIMARY KEY,
                attendance_record_id INT NOT NULL,
                project_id INT NOT NULL,
                hours DECIMAL(4,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (attendance_record_id) REFERENCES attendance_records(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        db.commit()
        
        # 初期データの投入（既に存在する場合はスキップ）
        # テスト用の課長アカウント
        existing_manager = db.execute_query(
            "SELECT id FROM employees WHERE email = %s",
            ('manager@example.com',)
        )
        
        if not existing_manager:
            # パスワードをハッシュ化（簡易的な実装）
            password_hash = hashlib.sha256('password123'.encode()).hexdigest()
            db.execute_query("""
                INSERT INTO employees (email, password, name, role)
                VALUES (%s, %s, %s, %s)
            """, ('manager@example.com', password_hash, '課長 太郎', 'manager'))
        
        # テスト用の社員アカウント
        existing_employee = db.execute_query(
            "SELECT id FROM employees WHERE email = %s",
            ('employee@example.com',)
        )
        
        if not existing_employee:
            password_hash = hashlib.sha256('password123'.encode()).hexdigest()
            db.execute_query("""
                INSERT INTO employees (email, password, name, role)
                VALUES (%s, %s, %s, %s)
            """, ('employee@example.com', password_hash, '社員 花子', 'employee'))
        
        # テスト用のプロジェクト
        existing_project = db.execute_query(
            "SELECT id FROM projects WHERE name = %s",
            ('プロジェクトA',)
        )
        
        if not existing_project:
            db.execute_query("""
                INSERT INTO projects (name)
                VALUES (%s)
            """, ('プロジェクトA',))
        
        db.commit()
        print("データベースの初期化が完了しました。")
        
    except Exception as e:
        db.rollback()
        print(f"データベース初期化エラー: {str(e)}")
        raise
    finally:
        db.close_connection()


if __name__ == "__main__":
    init_database()

