"""
データベースステータスページのUIテスト

FlaskアプリケーションのDBステータスページ（/db/status）のUIテストを実装します。
"""

from selenium.webdriver.common.by import By
from tests.ui.base_test import BaseSeleniumTest


class TestDbStatusPage(BaseSeleniumTest):
    """
    データベースステータスページのテストクラス
    
    DBステータスページの表示内容と動作をテストします。
    """
    
    def test_db_status_page_content(self):
        """
        DBステータスページにMySQL接続成功メッセージが表示されることを確認するテスト
        
        データベース接続が正常に行われている場合、成功メッセージが表示されることを検証します。
        """
        self.driver.get(f"{self.base_url}/db/status")
        
        # ページのbodyを取得
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        
        # MySQL接続成功メッセージが含まれていることを確認
        assert "MySQL接続成功" in body_text or "バージョン" in body_text, \
            f"期待されるDB接続メッセージが見つかりませんでした。実際のテキスト: {body_text}"
    
    def test_db_status_page_shows_version(self):
        """
        DBステータスページにMySQLバージョンが表示されることを確認するテスト
        
        データベースのバージョン情報が表示されることを検証します。
        """
        self.driver.get(f"{self.base_url}/db/status")
        
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        
        # バージョン情報が含まれていることを確認（8.0.43など）
        assert "8.0" in body_text or "バージョン" in body_text, \
            f"バージョン情報が見つかりませんでした。実際のテキスト: {body_text}"

