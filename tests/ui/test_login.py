"""
ログインページのUIテスト

FlaskアプリケーションのログインページのUIテストを実装します。
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.ui.base_test import BaseSeleniumTest
import time


class TestLoginPage(BaseSeleniumTest):
    """
    ログインページのテストクラス
    
    ログインページの表示内容と動作をテストします。
    """
    
    def test_login_page_display(self):
        """
        ログインページが正しく表示されることを確認するテスト
        
        ログインページにアクセスした際に、正しい内容が表示されることを検証します。
        """
        self.driver.get(f"{self.base_url}/login")
        
        # ページのタイトルを確認
        assert "ログイン" in self.driver.title or "勤怠管理システム" in self.driver.title
        
        # メールアドレス入力フィールドが存在することを確認
        email_input = self.wait_for_element((By.NAME, "email"))
        assert email_input is not None
        
        # パスワード入力フィールドが存在することを確認
        password_input = self.driver.find_element(By.NAME, "password")
        assert password_input is not None
    
    def test_login_success(self):
        """
        正しい認証情報でログインできることを確認するテスト
        
        テストアカウントでログインできることを検証します。
        """
        self.driver.get(f"{self.base_url}/login")
        
        # ログイン情報を入力
        email_input = self.wait_for_element((By.NAME, "email"))
        password_input = self.driver.find_element(By.NAME, "password")
        
        email_input.send_keys("manager@example.com")
        password_input.send_keys("password123")
        
        # ログインボタンをクリック
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # ダッシュボードにリダイレクトされることを確認
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        # ページの内容を確認
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        assert "ダッシュボード" in body_text or "ようこそ" in body_text
    
    def test_login_failure(self):
        """
        間違った認証情報でログインできないことを確認するテスト
        
        不正な認証情報でログインしようとした場合、エラーメッセージが表示されることを検証します。
        """
        self.driver.get(f"{self.base_url}/login")
        
        # 間違ったログイン情報を入力
        email_input = self.wait_for_element((By.NAME, "email"))
        password_input = self.driver.find_element(By.NAME, "password")
        
        email_input.send_keys("wrong@example.com")
        password_input.send_keys("wrongpassword")
        
        # ログインボタンをクリック
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # エラーメッセージが表示されることを確認
        time.sleep(1)  # フラッシュメッセージの表示を待つ
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        assert "正しくありません" in body_text or "エラー" in body_text

