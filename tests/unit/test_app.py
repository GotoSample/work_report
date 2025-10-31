"""
app.pyの単体テスト

Flaskアプリケーションの各エンドポイントの動作をテストします。
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# コンテナ内のパス構造に対応するため、パスを追加
# コンテナ内では/usr/src/appがワーキングディレクトリなので、そこをパスに追加
sys.path.insert(0, '/usr/src/app')
# ローカル環境用のフォールバック
if not os.path.exists('/usr/src/app/app.py'):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from app import app


class TestApp:
    """
    Flaskアプリケーションのテストクラス
    
    各エンドポイントの動作をテストします。
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
    
    def test_hello_flask(self):
        """
        hello_flaskエンドポイントのテスト
        
        メインページにアクセスした際に、ログインページにリダイレクトされることを確認します。
        """
        response = self.client.get('/')
        # ログインページにリダイレクトされる（302）または直接ログインページが表示される（200）
        assert response.status_code in [200, 302]
        if response.status_code == 302:
            assert '/login' in response.location or '/login' in response.headers.get('Location', '')
        else:
            assert 'ログイン' in response.data.decode('utf-8')
    
    @patch('app.DBAccess')
    def test_db_status_success(self, mock_dbaccess):
        """
        db_statusエンドポイントの正常系テスト
        
        データベース接続が成功し、バージョン情報が返されることを確認します。
        """
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [{'version': '8.0.43'}]
        mock_dbaccess.return_value = mock_db_instance
        
        response = self.client.get('/db/status')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'MySQL接続成功' in response_text
        assert 'バージョン' in response_text
        assert '8.0.43' in response_text
        
        # DBAccessが正しく呼ばれたことを確認
        mock_dbaccess.assert_called_once()
        mock_db_instance.execute_query.assert_called_once_with("SELECT VERSION() as version")
        mock_db_instance.close_connection.assert_called_once()
    
    @patch('app.DBAccess')
    def test_db_status_no_results(self, mock_dbaccess):
        """
        db_statusエンドポイントの異常系テスト（結果なし）
        
        クエリ結果が空の場合の処理を確認します。
        """
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []
        mock_dbaccess.return_value = mock_db_instance
        
        response = self.client.get('/db/status')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'MySQL接続エラー' in response_text
        assert '結果が取得できませんでした' in response_text
    
    @patch('app.DBAccess')
    def test_db_status_none_results(self, mock_dbaccess):
        """
        db_statusエンドポイントの異常系テスト（None結果）
        
        クエリ結果がNoneの場合の処理を確認します。
        """
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = None
        mock_dbaccess.return_value = mock_db_instance
        
        response = self.client.get('/db/status')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'MySQL接続エラー' in response_text
        assert '結果が取得できませんでした' in response_text
    
    @patch('app.DBAccess')
    def test_db_status_empty_dict_in_results(self, mock_dbaccess):
        """
        db_statusエンドポイントの異常系テスト（空辞書）
        
        クエリ結果に空辞書が含まれる場合の処理を確認します。
        """
        # モックの設定
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [{}]
        mock_dbaccess.return_value = mock_db_instance
        
        response = self.client.get('/db/status')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'MySQL接続成功' in response_text
        assert 'Unknown' in response_text
    
    @patch('app.DBAccess')
    def test_db_status_exception(self, mock_dbaccess):
        """
        db_statusエンドポイントの異常系テスト（例外発生）
        
        データベース接続時に例外が発生した場合の処理を確認します。
        """
        # モックの設定: 例外を発生させる
        mock_dbaccess.side_effect = Exception('Connection failed')
        
        response = self.client.get('/db/status')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'MySQL接続エラー' in response_text
        assert 'Connection failed' in response_text

