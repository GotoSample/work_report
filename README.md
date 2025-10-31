# Flask MySQL Docker プロジェクト

FlaskとMySQLを使用したWebアプリケーションをDocker Compose環境で実行するプロジェクトです。Seleniumを使用したUIテストも含まれています。

## プロジェクト概要

このプロジェクトは、以下の技術を使用したWebアプリケーションの開発環境を提供します：

- **Flask**: Python Webフレームワーク
- **MySQL**: リレーショナルデータベース
- **phpMyAdmin**: MySQL管理ツール
- **Selenium**: UIテスト自動化ツール
- **Docker Compose**: マルチコンテナ環境の管理

## 技術スタック

- **バックエンドフレームワーク**: Flask 2.1.0
- **データベース**: MySQL 8.0
- **Pythonバージョン**: 3.10
- **コンテナ環境**: Docker & Docker Compose
- **テストフレームワーク**: pytest, Selenium

## 機能

- Flask Webアプリケーションの実行
- MySQLデータベースへの接続と操作
- phpMyAdminによるデータベース管理
- Seleniumを使用したUIテスト自動化

## プロジェクト構造

```
flask_MySQL/
├── compose.yaml          # Docker Compose設定ファイル
├── Dockerfile           # Flaskアプリケーション用のDockerイメージ定義
├── src/
│   └── app.py          # Flaskアプリケーションのメインファイル
├── tests/               # テストコード
│   ├── __init__.py
│   ├── conftest.py     # pytest設定ファイル
│   ├── requirements.txt # テスト依存パッケージ
│   ├── README.md        # テスト実行方法
│   └── ui/              # UIテストコード
│       ├── __init__.py
│       ├── base_test.py         # ベーステストクラス
│       ├── test_home_page.py    # ホームページのテスト
│       └── test_db_status.py    # DBステータスページのテスト
├── AGENTS.md           # AIエージェント用ガイドライン
└── README.md           # このファイル
```

## 前提条件

以下のソフトウェアがインストールされている必要があります：

- Docker (version 20.10以上)
- Docker Compose (version 2.0以上)

## セットアップ方法

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd flask_MySQL
```

### 2. Docker Composeでコンテナを起動

```bash
# コンテナのビルドと起動（バックグラウンド）
docker compose up -d --build

# ログを表示しながら起動
docker compose up --build
```

### 3. サービスの確認

すべてのサービスが正常に起動していることを確認します：

```bash
docker compose ps
```

以下のサービスが起動します：
- **web**: Flaskアプリケーション (ポート 5000)
- **db**: MySQLデータベース (ポート 3306)
- **phpmyadmin**: phpMyAdmin管理ツール (ポート 8080)
- **selenium**: Selenium WebDriver (ポート 4444, 7900)

## 使用方法

### Flaskアプリケーションへのアクセス

ブラウザで以下のURLにアクセスします：

- **ホームページ**: http://localhost:5000/
- **DBステータスページ**: http://localhost:5000/db/status

### phpMyAdminでのデータベース管理

以下のURLにアクセスしてphpMyAdminにログインします：

- **URL**: http://localhost:8080
- **サーバー**: db
- **ユーザー名**: root
- **パスワード**: rootpassword

### Seleniumの使用

Selenium WebDriverは以下のポートで利用可能です：

- **WebDriver Hub**: http://localhost:4444
- **VNC（リモートデスクトップ）**: http://localhost:7900

## Docker Composeコマンド

### コンテナの起動と停止

```bash
# すべてのサービスを起動
docker compose up -d

# すべてのサービスを停止
docker compose down

# すべてのサービスを停止（ボリュームも削除）
docker compose down -v

# コンテナを再ビルドして起動
docker compose up -d --build
```

### ログの確認

```bash
# すべてのサービスのログを表示
docker compose logs -f

# 特定のサービスのログを表示
docker compose logs -f web
docker compose logs -f db
```

### コンテナ内でコマンドを実行

```bash
# webコンテナでシェルを実行
docker compose exec web bash

# dbコンテナでMySQLに接続
docker compose exec db mysql -u root -prootpassword flask_db
```

## APIエンドポイント

### GET /

Flaskアプリケーションのホームページです。

**レスポンス例:**
```
Hello Flask!
```

### GET /db/status

MySQLデータベースへの接続状態を確認します。

**レスポンス例:**
```
MySQL接続成功! バージョン: 8.0.43
```

## テストの実行

### UIテストの実行

Seleniumを使用したUIテストを実行します：

```bash
# すべてのUIテストを実行
docker compose exec web python -m pytest tests/ui/ -v

# 特定のテストファイルを実行
docker compose exec web python -m pytest tests/ui/test_home_page.py -v

# テスト結果を詳細に表示
docker compose exec web python -m pytest tests/ui/ -v -s
```

### テスト結果の例

```
============================= test session starts ==============================
platform linux -- Python 3.10.19, pytest-8.4.2
collected 4 items

tests/ui/test_db_status.py::TestDbStatusPage::test_db_status_page_content PASSED
tests/ui/test_db_status.py::TestDbStatusPage::test_db_status_page_shows_version PASSED
tests/ui/test_home_page.py::TestHomePage::test_home_page_title PASSED
tests/ui/test_home_page.py::TestHomePage::test_home_page_status_code PASSED

============================== 4 passed in 6.42s ===============================
```

## 環境変数

### webサービス

- `FLASK_ENV`: Flask環境（デフォルト: development）
- `FLASK_APP`: Flaskアプリケーションファイル（デフォルト: app.py）
- `MYSQL_HOST`: MySQLホスト（デフォルト: db）
- `MYSQL_USER`: MySQLユーザー名（デフォルト: root）
- `MYSQL_PASSWORD`: MySQLパスワード（デフォルト: rootpassword）
- `MYSQL_DATABASE`: MySQLデータベース名（デフォルト: flask_db）

### dbサービス

- `MYSQL_ROOT_PASSWORD`: MySQL rootパスワード（デフォルト: rootpassword）
- `MYSQL_DATABASE`: 作成するデータベース名（デフォルト: flask_db）
- `MYSQL_USER`: 作成するユーザー名（デフォルト: flask_user）
- `MYSQL_PASSWORD`: 作成するユーザーのパスワード（デフォルト: flask_password）

## データベース接続情報

### 接続情報

- **ホスト**: localhost (外部から) / db (コンテナ間)
- **ポート**: 3306
- **データベース名**: flask_db
- **ユーザー名**: root または flask_user
- **パスワード**: rootpassword または flask_password

### データベースの永続化

MySQLデータは `mysql_data` という名前のDockerボリュームに保存されます。コンテナを削除してもデータは保持されます。

## トラブルシューティング

### コンテナが起動しない場合

```bash
# コンテナの状態を確認
docker compose ps

# ログを確認
docker compose logs

# コンテナを再作成
docker compose down
docker compose up -d --build
```

### ポートが既に使用されている場合

`compose.yaml` のポート設定を変更してください：

```yaml
ports:
  - "5001:5000"  # 5000の代わりに5001を使用
```

### データベース接続エラー

```bash
# MySQLコンテナが起動しているか確認
docker compose ps db

# MySQLコンテナのログを確認
docker compose logs db

# MySQLコンテナを再起動
docker compose restart db
```

### テストが失敗する場合

```bash
# すべてのサービスが起動しているか確認
docker compose ps

# Seleniumコンテナが正常に動作しているか確認
curl http://localhost:4444/wd/hub/status

# テスト用のパッケージがインストールされているか確認
docker compose exec web python -m pip list | grep -E "(selenium|pytest)"
```

## 開発ガイドライン

### コードスタイル

- すべてのクラスには日本語のクラスコメントを記述してください
- すべてのメソッドには日本語のメソッドコメントを記述してください
- docstringのコメントを記述してください

### 新しいテストの追加

新しいUIテストを追加する場合は、`tests/ui/` ディレクトリに `test_*.py` という形式でファイルを作成し、`BaseSeleniumTest` クラスを継承してください。

### ソースコードの変更

`src/app.py` を編集すると、ボリュームマウントにより変更が自動的に反映されます。Flaskアプリケーションの再起動は不要です（開発モードの場合）。

## ライセンス

このプロジェクトのライセンス情報をここに記載してください。

## 貢献

プルリクエストやイシューの報告を歓迎します。貢献する前に、コーディングスタイルガイドラインを確認してください。

## 更新履歴

- **2024-10-31**: プロジェクトの初期作成
  - Flask、MySQL、phpMyAdmin、Seleniumの統合
  - UIテストの実装

