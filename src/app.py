"""
勤怠管理システムのメインアプリケーション

Flaskを使用した勤怠管理システムのエントリーポイントです。
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from applications.DBAccess import DBAccess
from functools import wraps
from datetime import datetime, date, timedelta
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# データベースの初期化（起動時）
# Flask 2.x対応
try:
    from applications.db_init import init_database
    init_database()
except Exception as e:
    print(f"データベース初期化エラー（起動時）: {str(e)}")


def login_required(f):
    """
    ログイン必須デコレータ
    
    ログインしていないユーザーをログインページにリダイレクトします。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('ログインが必要です', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """
    課長権限必須デコレータ
    
    課長権限を持たないユーザーをアクセス拒否します。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'manager':
            flash('この機能は課長のみアクセスできます', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """
    インデックスページ
    
    Returns:
        str: インデックスページのHTML
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    ログインページ
    
    GET: ログインフォームを表示
    POST: ログイン処理を実行
    
    Returns:
        str: ログインページのHTML または ダッシュボードへのリダイレクト
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('メールアドレスとパスワードを入力してください', 'error')
            return render_template('login.html')
        
        db = DBAccess()
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            users = db.execute_query(
                "SELECT id, email, name, role FROM employees WHERE email = %s AND password = %s",
                (email, password_hash)
            )
            
            if users and len(users) > 0:
                user = users[0]
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                session['user_name'] = user['name']
                session['user_role'] = user['role']
                flash(f'ようこそ、{user["name"]}さん', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('メールアドレスまたはパスワードが正しくありません', 'error')
        except Exception as e:
            flash(f'ログインエラー: {str(e)}', 'error')
        finally:
            db.close_connection()
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    ログアウト処理
    
    Returns:
        Redirect: ログインページへのリダイレクト
    """
    session.clear()
    flash('ログアウトしました', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """
    ダッシュボードページ
    
    Returns:
        str: ダッシュボードページのHTML
    """
    db = DBAccess()
    try:
        # 今月の勤怠記録を取得
        today = date.today()
        first_day = today.replace(day=1)
        
        records = db.execute_query("""
            SELECT date, attendance_type, start_time, end_time, break_time
            FROM attendance_records
            WHERE employee_id = %s AND date >= %s
            ORDER BY date DESC
            LIMIT 10
        """, (session['user_id'], first_day))
        
        # timedeltaオブジェクトを文字列に変換
        from datetime import timedelta
        formatted_records = []
        for record in records:
            formatted_record = dict(record)
            # start_time, end_time, break_timeをフォーマット
            if formatted_record.get('start_time'):
                if isinstance(formatted_record['start_time'], timedelta):
                    total_seconds = int(formatted_record['start_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_record['start_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(formatted_record['start_time'], 'strftime'):
                    formatted_record['start_time'] = formatted_record['start_time'].strftime('%H:%M')
            
            if formatted_record.get('end_time'):
                if isinstance(formatted_record['end_time'], timedelta):
                    total_seconds = int(formatted_record['end_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_record['end_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(formatted_record['end_time'], 'strftime'):
                    formatted_record['end_time'] = formatted_record['end_time'].strftime('%H:%M')
            
            if formatted_record.get('break_time'):
                if isinstance(formatted_record['break_time'], timedelta):
                    total_seconds = int(formatted_record['break_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_record['break_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(formatted_record['break_time'], 'strftime'):
                    formatted_record['break_time'] = formatted_record['break_time'].strftime('%H:%M')
            
            formatted_records.append(formatted_record)
        
        return render_template('dashboard.html', records=formatted_records, user_name=session['user_name'])
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return render_template('dashboard.html', records=[], user_name=session.get('user_name', ''))
    finally:
        db.close_connection()


@app.route('/attendance/input', methods=['GET', 'POST'])
@login_required
def attendance_input():
    """
    勤怠入力ページ
    
    GET: 勤怠入力フォームを表示
    POST: 勤怠記録を保存
    
    Returns:
        str: 勤怠入力ページのHTML または ダッシュボードへのリダイレクト
    """
    db = DBAccess()
    
    try:
        if request.method == 'POST':
            record_date = request.form.get('date')
            attendance_type = request.form.get('attendance_type')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            break_time = request.form.get('break_time', '01:00:00')
            notes = request.form.get('notes', '')
            
            if not record_date or not attendance_type:
                flash('日付と出勤区分は必須です', 'error')
                return redirect(url_for('attendance_input'))
            
            # 既存の記録があるか確認
            existing = db.execute_query(
                "SELECT id FROM attendance_records WHERE employee_id = %s AND date = %s",
                (session['user_id'], record_date)
            )
            
            # プロジェクト作業時間の取得
            project_hours = []
            projects = db.execute_query("SELECT id, name FROM projects")
            for project in projects:
                hours_key = f'project_hours_{project["id"]}'
                hours = request.form.get(hours_key)
                if hours and float(hours) > 0:
                    project_hours.append((project['id'], float(hours)))
            
            record_id = None
            if existing:
                # 更新
                record_id = existing[0]['id']
                db.execute_query("""
                    UPDATE attendance_records
                    SET attendance_type = %s, start_time = %s, end_time = %s,
                        break_time = %s, notes = %s
                    WHERE id = %s
                """, (attendance_type, start_time, end_time, break_time, notes, record_id))
                flash('勤怠記録を更新しました', 'success')
            else:
                # 新規作成
                cursor = db.get_cursor()
                cursor.execute("""
                    INSERT INTO attendance_records
                    (employee_id, date, attendance_type, start_time, end_time, break_time, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (session['user_id'], record_date, attendance_type, start_time, end_time, break_time, notes))
                record_id = cursor.lastrowid
                flash('勤怠記録を保存しました', 'success')
            
            db.commit()
            
            # プロジェクト作業時間の処理（既存の記録を削除してから追加）
            if record_id:
                # 既存のプロジェクト作業時間を削除
                db.execute_query(
                    "DELETE FROM project_hours WHERE attendance_record_id = %s",
                    (record_id,)
                )
                
                # 新しいプロジェクト作業時間を追加
                for project_id, hours in project_hours:
                    db.execute_query("""
                        INSERT INTO project_hours (attendance_record_id, project_id, hours)
                        VALUES (%s, %s, %s)
                    """, (record_id, project_id, hours))
                
                db.commit()
            
            return redirect(url_for('dashboard'))
        
        # GETリクエスト: フォームを表示
        projects = db.execute_query("SELECT id, name FROM projects ORDER BY name")
        date_str = request.args.get('date', date.today().isoformat())
        
        # 指定日の記録があれば取得
        today_record = db.execute_query("""
            SELECT ar.*
            FROM attendance_records ar
            WHERE ar.employee_id = %s AND ar.date = %s
            LIMIT 1
        """, (session['user_id'], date_str))
        
        record_data = None
        project_hours_list = []
        
        if today_record:
            record_data = dict(today_record[0])
            # timedeltaオブジェクトを文字列に変換（テンプレートで使用するため）
            from datetime import timedelta
            
            # start_time, end_time, break_timeをフォーマット
            if record_data.get('start_time'):
                if isinstance(record_data['start_time'], timedelta):
                    total_seconds = int(record_data['start_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    record_data['start_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(record_data['start_time'], 'strftime'):
                    record_data['start_time'] = record_data['start_time'].strftime('%H:%M')
            
            if record_data.get('end_time'):
                if isinstance(record_data['end_time'], timedelta):
                    total_seconds = int(record_data['end_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    record_data['end_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(record_data['end_time'], 'strftime'):
                    record_data['end_time'] = record_data['end_time'].strftime('%H:%M')
            
            if record_data.get('break_time'):
                if isinstance(record_data['break_time'], timedelta):
                    total_seconds = int(record_data['break_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    record_data['break_time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(record_data['break_time'], 'strftime'):
                    record_data['break_time'] = record_data['break_time'].strftime('%H:%M')
            
            # プロジェクト作業時間を取得
            ph_data = db.execute_query("""
                SELECT project_id, hours
                FROM project_hours
                WHERE attendance_record_id = %s
            """, (record_data['id'],))
            project_hours_list = [(ph['project_id'], ph['hours']) for ph in ph_data]
        else:
            record_data = None
            project_hours_list = []
        
        # プロジェクトに作業時間をマッピング
        for project in projects:
            project['hours'] = None
            for ph_id, ph_hours in project_hours_list:
                if project['id'] == ph_id:
                    project['hours'] = ph_hours
                    break
        
        return render_template('attendance_input.html', 
                             projects=projects, 
                             today=date_str,
                             record=record_data)
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    finally:
        db.close_connection()


@app.route('/attendance/view/<date_str>')
@login_required
def attendance_view(date_str):
    """
    勤怠記録の詳細表示
    
    Args:
        date_str: 日付文字列 (YYYY-MM-DD)
    
    Returns:
        str: 勤怠記録詳細ページのHTML
    """
    db = DBAccess()
    try:
        record = db.execute_query("""
            SELECT ar.*, e.name as employee_name
            FROM attendance_records ar
            JOIN employees e ON ar.employee_id = e.id
            WHERE ar.date = %s AND (ar.employee_id = %s OR %s = 'manager')
            LIMIT 1
        """, (date_str, session['user_id'], session['user_role']))
        
        if not record:
            flash('勤怠記録が見つかりません', 'error')
            return redirect(url_for('dashboard'))
        
        # timedeltaオブジェクトを文字列に変換
        from datetime import timedelta
        formatted_record = dict(record[0])
        
        # start_time, end_time, break_timeをフォーマット
        if formatted_record.get('start_time'):
            if isinstance(formatted_record['start_time'], timedelta):
                total_seconds = int(formatted_record['start_time'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                formatted_record['start_time'] = f"{hours:02d}:{minutes:02d}"
            elif hasattr(formatted_record['start_time'], 'strftime'):
                formatted_record['start_time'] = formatted_record['start_time'].strftime('%H:%M')
        
        if formatted_record.get('end_time'):
            if isinstance(formatted_record['end_time'], timedelta):
                total_seconds = int(formatted_record['end_time'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                formatted_record['end_time'] = f"{hours:02d}:{minutes:02d}"
            elif hasattr(formatted_record['end_time'], 'strftime'):
                formatted_record['end_time'] = formatted_record['end_time'].strftime('%H:%M')
        
        if formatted_record.get('break_time'):
            if isinstance(formatted_record['break_time'], timedelta):
                total_seconds = int(formatted_record['break_time'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                formatted_record['break_time'] = f"{hours:02d}:{minutes:02d}"
            elif hasattr(formatted_record['break_time'], 'strftime'):
                formatted_record['break_time'] = formatted_record['break_time'].strftime('%H:%M')
        
        # プロジェクト作業時間を取得
        project_hours = db.execute_query("""
            SELECT ph.*, p.name as project_name
            FROM project_hours ph
            JOIN projects p ON ph.project_id = p.id
            WHERE ph.attendance_record_id = %s
        """, (formatted_record['id'],))
        
        return render_template('attendance_view.html', 
                             record=formatted_record, 
                             project_hours=project_hours)
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    finally:
        db.close_connection()


@app.route('/employees', methods=['GET'])
@login_required
@manager_required
def employees_list():
    """
    社員一覧ページ（課長のみ）
    
    Returns:
        str: 社員一覧ページのHTML
    """
    db = DBAccess()
    try:
        employees = db.execute_query("""
            SELECT id, email, name, role, created_at
            FROM employees
            ORDER BY name
        """)
        return render_template('employees_list.html', employees=employees)
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return render_template('employees_list.html', employees=[])
    finally:
        db.close_connection()


@app.route('/employees/create', methods=['GET', 'POST'])
@login_required
@manager_required
def employee_create():
    """
    社員作成ページ（課長のみ）
    
    GET: 社員作成フォームを表示
    POST: 社員を作成
    
    Returns:
        str: 社員作成ページのHTML または 社員一覧へのリダイレクト
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role', 'employee')
        
        if not email or not password or not name:
            flash('すべての項目を入力してください', 'error')
            return render_template('employee_form.html', employee=None)
        
        db = DBAccess()
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            db.execute_query("""
                INSERT INTO employees (email, password, name, role)
                VALUES (%s, %s, %s, %s)
            """, (email, password_hash, name, role))
            db.commit()
            flash('社員を作成しました', 'success')
            return redirect(url_for('employees_list'))
        except Exception as e:
            db.rollback()
            flash(f'エラー: {str(e)}', 'error')
        finally:
            db.close_connection()
    
    return render_template('employee_form.html', employee=None)


@app.route('/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def employee_edit(employee_id):
    """
    社員編集ページ（課長のみ）
    
    Args:
        employee_id: 社員ID
    
    Returns:
        str: 社員編集ページのHTML または 社員一覧へのリダイレクト
    """
    db = DBAccess()
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            role = request.form.get('role', 'employee')
            
            if not email or not name:
                flash('メールアドレスと名前は必須です', 'error')
                return redirect(url_for('employee_edit', employee_id=employee_id))
            
            if password:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                db.execute_query("""
                    UPDATE employees
                    SET email = %s, password = %s, name = %s, role = %s
                    WHERE id = %s
                """, (email, password_hash, name, role, employee_id))
            else:
                db.execute_query("""
                    UPDATE employees
                    SET email = %s, name = %s, role = %s
                    WHERE id = %s
                """, (email, name, role, employee_id))
            
            db.commit()
            flash('社員情報を更新しました', 'success')
            return redirect(url_for('employees_list'))
        
        # GETリクエスト
        employees = db.execute_query(
            "SELECT id, email, name, role FROM employees WHERE id = %s",
            (employee_id,)
        )
        
        if not employees:
            flash('社員が見つかりません', 'error')
            return redirect(url_for('employees_list'))
        
        return render_template('employee_form.html', employee=employees[0])
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return redirect(url_for('employees_list'))
    finally:
        db.close_connection()


@app.route('/employees/delete/<int:employee_id>', methods=['POST'])
@login_required
@manager_required
def employee_delete(employee_id):
    """
    社員削除処理（課長のみ）
    
    Args:
        employee_id: 社員ID
    
    Returns:
        Redirect: 社員一覧へのリダイレクト
    """
    db = DBAccess()
    try:
        db.execute_query("DELETE FROM employees WHERE id = %s", (employee_id,))
        db.commit()
        flash('社員を削除しました', 'success')
    except Exception as e:
        db.rollback()
        flash(f'エラー: {str(e)}', 'error')
    finally:
        db.close_connection()
    
    return redirect(url_for('employees_list'))


@app.route('/report/monthly')
@login_required
@manager_required
def monthly_report():
    """
    月次レポートページ（課長のみ）
    
    Returns:
        str: 月次レポートページのHTML
    """
    db = DBAccess()
    try:
        # 年月の取得（デフォルトは今月）
        year = request.args.get('year', date.today().year)
        month = request.args.get('month', date.today().month)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            year = date.today().year
            month = date.today().month
        
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        # 全社員の勤怠データを取得
        report_data = db.execute_query("""
            SELECT 
                e.id as employee_id,
                e.name as employee_name,
                COUNT(ar.id) as attendance_days,
                SUM(TIME_TO_SEC(TIMEDIFF(ar.end_time, ar.start_time)) / 3600) as total_hours,
                SUM(TIME_TO_SEC(ar.break_time) / 3600) as total_break_hours
            FROM employees e
            LEFT JOIN attendance_records ar ON e.id = ar.employee_id 
                AND ar.date >= %s AND ar.date <= %s
            GROUP BY e.id, e.name
            ORDER BY e.name
        """, (first_day, last_day))
        
        return render_template('monthly_report.html', 
                             report_data=report_data,
                             year=year,
                             month=month)
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return render_template('monthly_report.html', 
                             report_data=[],
                             year=date.today().year,
                             month=date.today().month)
    finally:
        db.close_connection()


@app.route('/db/status')
def db_status():
    """
    データベース接続状態を確認するエンドポイント
    
    Returns:
        str: データベース接続状態のメッセージ
    """
    try:
        db = DBAccess()
        results = db.execute_query("SELECT VERSION() as version")
        db.close_connection()
        if results and len(results) > 0:
            version = results[0]['version'] if results[0] else 'Unknown'
            return f'MySQL接続成功! バージョン: {version}'
        else:
            return 'MySQL接続エラー: 結果が取得できませんでした'
    except Exception as e:
        return f'MySQL接続エラー: {str(e)}'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
