# Selenium UIテスト

このディレクトリには、FlaskアプリケーションのUIテストコードが含まれています。

## ディレクトリ構造

```
tests/
├── __init__.py                  # テストモジュール初期化ファイル
├── conftest.py                  # pytest設定ファイル
├── requirements.txt             # テスト実行に必要なパッケージ
├── README.md                    # このファイル
└── ui/                          # UIテスト専用ディレクトリ
    ├── __init__.py
    ├── base_test.py             # ベーステストクラス
    ├── test_home_page.py        # ホームページのテスト
    └── test_db_status.py        # DBステータスページのテスト
```

## テストの実行方法

### Docker Compose環境での実行

1. すべてのサービス（web, db, selenium）が起動していることを確認
```bash
docker compose ps
```

2. テストコンテナを起動して実行
```bash
# テストコンテナを追加して実行する場合
docker compose run --rm test python -m pytest tests/ui/ -v
```

### ローカル環境での実行（推奨しない）

```bash
# 依存関係のインストール
pip install -r tests/requirements.txt

# テストの実行
pytest tests/ui/ -v
```

## テストファイルの説明

### base_test.py
- Seleniumテストのベースクラス
- WebDriverの初期化とクリーンアップを管理
- 共通のメソッドを提供

### test_home_page.py
- ホームページ（/）のテスト
- ページの表示内容を検証

### test_db_status.py
- DBステータスページ（/db/status）のテスト
- データベース接続状態を検証

## 環境変数

テスト実行時に以下の環境変数を設定できます：

- `SELENIUM_HUB_URL`: Selenium HubのURL（デフォルト: `http://selenium:4444/wd/hub`）
- `TEST_BASE_URL`: テスト対象のベースURL（デフォルト: `http://web:5000`）

## 注意事項

- テストはDocker Compose環境で実行することを推奨します
- Seleniumコンテナが起動している必要があります
- Flaskアプリケーション（web）が起動している必要があります

