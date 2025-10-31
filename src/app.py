from flask import Flask
import os
import pymysql

app = Flask(__name__)

def get_db_connection():
    """
    MySQLデータベースへの接続を取得する関数
    
    Returns:
        pymysql.Connection: MySQLデータベースへの接続オブジェクト
    """
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'flask_db'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        return None

@app.route('/')
def hello_flask():
    """
    メインページのハンドラー
    
    Returns:
        str: レスポンスメッセージ
    """
    return 'Hello Flask!'

@app.route('/db/status')
def db_status():
    """
    データベース接続状態を確認するエンドポイント
    
    Returns:
        str: データベース接続状態のメッセージ
    """
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION() as version")
                result = cursor.fetchone()
                version = result['version'] if result else 'Unknown'
            connection.close()
            return f'MySQL接続成功! バージョン: {version}'
        except Exception as e:
            return f'MySQL接続エラー: {str(e)}'
    else:
        return 'MySQL接続に失敗しました'
