"""
pytest設定ファイル

pytestの共通設定とfixtureを定義します。
"""

import pytest
import os


@pytest.fixture(scope="session")
def selenium_hub_url():
    """
    Selenium HubのURLを取得するfixture
    
    Returns:
        str: Selenium HubのURL
    """
    return os.getenv('SELENIUM_HUB_URL', 'http://selenium:4444/wd/hub')


@pytest.fixture(scope="session")
def test_base_url():
    """
    テスト対象のベースURLを取得するfixture
    
    Returns:
        str: テスト対象のベースURL
    """
    return os.getenv('TEST_BASE_URL', 'http://web:5000')

