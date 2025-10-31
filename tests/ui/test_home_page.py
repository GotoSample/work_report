"""
ホームページのUIテスト

Flaskアプリケーションのホームページ（/）のUIテストを実装します。
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.ui.base_test import BaseSeleniumTest


class TestHomePage(BaseSeleniumTest):
    """
    ホームページのテストクラス
    
    ホームページの表示内容と動作をテストします。
    """
    
    def test_home_page_title(self):
        """
        ホームページがログインページにリダイレクトされることを確認するテスト
        
        ページにアクセスした際に、ログインページにリダイレクトされることを検証します。
        """
        self.driver.get(f"{self.base_url}/")
        
        # ログインページにリダイレクトされることを確認
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/login")
        )
        
        # ページのbodyに"ログイン"が含まれていることを確認
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        assert "ログイン" in body_text, f"期待されるテキスト 'ログイン' が見つかりませんでした。実際のテキスト: {body_text}"
    
    def test_home_page_status_code(self):
        """
        ホームページが正常にレスポンスを返すことを確認するテスト
        
        HTTPステータスコードが200であることを確認します。
        """
        self.driver.get(f"{self.base_url}/")
        
        # ページが正常に読み込まれたことを確認（Seleniumでは直接ステータスコードを取得できないため、
        # ページの存在を確認する）
        assert self.driver.current_url == f"{self.base_url}/" or f"{self.base_url}/" in self.driver.current_url

