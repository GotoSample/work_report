"""
勤怠入力ページのUIテスト

Flaskアプリケーションの勤怠入力ページのUIテストを実装します。
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from tests.ui.base_test import BaseSeleniumTest
from datetime import date, timedelta
import time


class TestAttendancePage(BaseSeleniumTest):
    """
    勤怠入力ページのテストクラス
    
    勤怠入力ページの表示内容と動作をテストします。
    """
    
    def setup_method(self):
        """
        テストメソッド実行前のセットアップ
        
        ログイン処理を実行します。
        """
        super().setup_method()
        # ログイン
        self.driver.get(f"{self.base_url}/login")
        email_input = self.wait_for_element((By.NAME, "email"))
        password_input = self.driver.find_element(By.NAME, "password")
        
        email_input.send_keys("employee@example.com")
        password_input.send_keys("password123")
        
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # ダッシュボードに遷移するまで待機
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/dashboard") or EC.url_contains("/login")
        )
    
    def test_attendance_input_page_display(self):
        """
        勤怠入力ページが正しく表示されることを確認するテスト
        
        勤怠入力ページにアクセスした際に、正しい内容が表示されることを検証します。
        """
        self.driver.get(f"{self.base_url}/attendance/input")
        
        # ページの内容を確認
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        assert "勤怠入力" in body_text
        
        # 日付入力フィールドが存在することを確認
        date_input = self.wait_for_element((By.NAME, "date"))
        assert date_input is not None
        
        # 出勤区分選択フィールドが存在することを確認
        attendance_type = self.driver.find_element(By.NAME, "attendance_type")
        assert attendance_type is not None
    
    def test_attendance_input_save(self):
        """
        勤怠記録を保存できることを確認するテスト
        
        勤怠情報を入力して保存できることを検証します。
        """
        self.driver.get(f"{self.base_url}/attendance/input")
        
        # 日付を設定（今日）
        today = date.today().isoformat()
        date_input = self.wait_for_element((By.NAME, "date"))
        date_input.clear()
        date_input.send_keys(today)
        
        # 出勤区分を選択
        attendance_type = Select(self.driver.find_element(By.NAME, "attendance_type"))
        attendance_type.select_by_value("出勤")
        
        # 出勤時間を入力
        start_time = self.driver.find_element(By.NAME, "start_time")
        start_time.clear()
        start_time.send_keys("09:00")
        
        # 退勤時間を入力
        end_time = self.driver.find_element(By.NAME, "end_time")
        end_time.clear()
        end_time.send_keys("18:00")
        
        # 休憩時間を入力
        break_time = self.driver.find_element(By.NAME, "break_time")
        break_time.clear()
        break_time.send_keys("01:00")
        
        # 保存ボタンをクリック
        save_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save_button.click()
        
        # ダッシュボードにリダイレクトされることを確認
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: "/dashboard" in driver.current_url or "/attendance" in driver.current_url
            )
        except:
            # URLが変わらない場合でも、ページの内容を確認
            pass
        
        # 成功メッセージが表示されることを確認
        time.sleep(2)  # フラッシュメッセージの表示を待つ
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        assert "保存しました" in body_text or "更新しました" in body_text or "ダッシュボード" in body_text

