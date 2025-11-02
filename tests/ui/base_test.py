"""
ベーステストクラス

Seleniumテストの共通機能を提供するベースクラス
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


class BaseSeleniumTest:
    """
    Seleniumテストのベースクラス
    
    すべてのUIテストクラスが継承する基底クラスです。
    WebDriverの初期化や共通のメソッドを提供します。
    """
    
    def setup_method(self):
        """
        テストメソッド実行前のセットアップ
        
        WebDriverを初期化し、ブラウザを起動します。
        Seleniumコンテナを使用する場合は、remote WebDriverを使用します。
        """
        # ベースURLの設定
        self.base_url = os.getenv('TEST_BASE_URL', 'http://web:5000')
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Seleniumコンテナへの接続
        selenium_hub_url = os.getenv('SELENIUM_HUB_URL', 'http://selenium:4444/wd/hub')
        
        self.driver = webdriver.Remote(
            command_executor=selenium_hub_url,
            options=chrome_options
        )
        self.driver.implicitly_wait(10)
    
    def teardown_method(self):
        """
        テストメソッド実行後のクリーンアップ
        
        WebDriverを終了し、ブラウザを閉じます。
        """
        if self.driver:
            self.driver.quit()
    
    def wait_for_element(self, locator, timeout=10):
        """
        要素が表示されるまで待機するメソッド
        
        Args:
            locator: 要素のロケーター（タプル形式 (By.ID, "id") など）
            timeout: タイムアウト時間（秒）
        
        Returns:
            WebElement: 見つかった要素
        """
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))
    
    def save_screenshot(self, filename):
        """
        スクリーンショットを保存するメソッド
        
        Args:
            filename: 保存するファイル名（SCREENSHOTS_DIR環境変数で指定されたディレクトリ、未指定ならscreenshots/ディレクトリに保存されます）
        """
        # スクリーンショット保存ディレクトリを環境変数で指定可能に
        screenshots_dir = os.getenv("SCREENSHOTS_DIR", "screenshots")
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        # ファイルパスを構築
        filepath = os.path.join(screenshots_dir, filename)
        
        # スクリーンショットを保存
        self.driver.save_screenshot(filepath)

