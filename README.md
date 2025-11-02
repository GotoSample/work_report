# 勤怠管理システム

社員の勤怠管理を行うWebアプリケーションです。FlaskとMySQLを使用し、Dockerコンテナ環境で動作します。
社員の出勤・退勤記録、勤怠状況の管理、レポート生成などの機能を提供します。

## プロジェクト概要

このプロジェクトは、以下の技術を使用した勤怠管理システムです：

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

## システム機能

### 機能一覧

#### 1. 社員認証機能
- メールアドレスとパスワードによるログイン
- ログアウト機能
- セッション管理

#### 2. 勤怠入力機能（社員・課長共通）
- 日別の勤怠情報入力
  - 出勤時間（15分単位）
  - 退勤時間（15分単位）
  - 休憩時間（15分単位）
  - 特記事項
  - 出勤区分（出勤、遅刻、早退、午前休、午後休、一日休）
  - プロジェクト毎の作業時間記録

#### 3. 社員管理機能（課長のみ）
- 社員のCRUD機能（作成・読み取り・更新・削除）
- 社員一覧表示
- 社員情報の編集・削除

#### 4. 月次レポート機能（課長のみ）
- 月次レポートの出力
- 勤怠データの集計・表示

### 認証方法

- **認証方式**: メールアドレスとパスワード
- **ログイン情報**:
  - メールアドレス（社員のメールアドレス）
  - パスワード（各社員のパスワード）

### 権限管理

システムは以下の2つの権限レベルで構成されます：

#### 社員権限
- 勤怠登録のみ可能
- 自分の勤怠情報の入力・確認

#### 課長権限
- 勤怠登録（社員と同等）
- 社員のCRUD機能（作成・読み取り・更新・削除）
- 月次レポートの出力
- 社員管理機能全般

### 勤怠管理の詳細

#### 記録項目（日別）
- **出勤時間**: 15分単位で記録
- **退勤時間**: 15分単位で記録
- **休憩時間**: 15分単位で記録
- **特記事項**: テキストで記録
- **出勤区分**: 以下のいずれかを選択
  - 出勤
  - 遅刻
  - 早退
  - 午前休
  - 午後休
  - 一日休
- **プロジェクト毎の作業時間**: プロジェクト単位で作業時間を記録

#### 時間の扱い
- すべての時間は15分単位で管理
- 例: 09:00, 09:15, 09:30, 09:45 など

## プロジェクト構造

```
work_report/
├── compose.yaml              # Docker Compose設定ファイル
├── Dockerfile               # Flaskアプリケーション用のDockerイメージ定義
├── src/
│   ├── app.py              # Flaskアプリケーションのメインファイル
│   ├── applications/
│   │   ├── db_init.py      # データベース初期化スクリプト
│   │   └── DBAccess.py     # データベースアクセスクラス
│   ├── templates/          # HTMLテンプレート
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── attendance_input.html
│   │   ├── attendance_view.html
│   │   ├── employees_list.html
│   │   ├── employee_form.html
│   │   └── monthly_report.html
│   └── tests/              # テストコード（src配下）
├── tests/                  # テストコード（プロジェクトルート）
│   ├── __init__.py
│   ├── conftest.py         # pytest設定ファイル
│   ├── requirements.txt    # テスト依存パッケージ
│   ├── README.md           # テスト実行方法
│   ├── unit/               # 単体テスト
│   │   ├── __init__.py
│   │   ├── test_app.py
│   │   ├── test_attendance_system.py
│   │   ├── test_dbaccess.py
│   │   └── test_time_formatting.py
│   ├── integration/        # 結合テスト
│   │   └── test_time_formatting_integration.py
│   └── ui/                 # UIテスト
│       ├── __init__.py
│       ├── base_test.py
│       ├── test_home_page.py
│       ├── test_db_status.py
│       ├── test_login.py
│       └── test_attendance.py
├── docs/                   # 設計書
│   └── 設計書一覧.md       # 設計書一覧
├── AGENTS.md               # AIエージェント用ガイドライン
└── README.md               # このファイル
```

## 前提条件

以下のソフトウェアがインストールされている必要があります：

- Docker (version 20.10以上)
- Docker Compose (version 2.0以上)

## セットアップ方法

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd work_report
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

- **ログインページ**: http://localhost:5000/login
- **ダッシュボード**: http://localhost:5000/dashboard
- **勤怠入力**: http://localhost:5000/attendance/input
- **DBステータスページ**: http://localhost:5000/db/status

### 初回ログイン

システム起動後、データベースが自動的に初期化されます。初期データが作成されている場合は、そのアカウントでログインしてください。
アカウントが存在しない場合は、課長権限でログインし、社員を作成してください。

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

### 認証関連

#### GET /
インデックスページ。ログイン済みの場合はダッシュボードにリダイレクトします。

#### GET /login
ログインフォームを表示します。

#### POST /login
ログイン処理を実行します。

**リクエストパラメータ:**
- `email`: メールアドレス
- `password`: パスワード

#### GET /logout
ログアウト処理を実行します。

### ダッシュボード

#### GET /dashboard
ログイン必須のダッシュボードページを表示します。今月の勤怠記録を表示します。

### 勤怠入力

#### GET /attendance/input
勤怠入力フォームを表示します（ログイン必須）。

**クエリパラメータ:**
- `date`: 日付 (YYYY-MM-DD形式、省略可)

#### POST /attendance/input
勤怠記録を保存します（ログイン必須）。

**リクエストパラメータ:**
- `date`: 日付 (YYYY-MM-DD形式)
- `attendance_type`: 出勤区分（出勤、遅刻、早退、午前休、午後休、一日休）
- `start_time`: 出勤時間 (HH:MM形式)
- `end_time`: 退勤時間 (HH:MM形式)
- `break_time`: 休憩時間 (HH:MM形式)
- `notes`: 特記事項（省略可）
- `project_hours_{project_id}`: プロジェクト毎の作業時間（省略可）

#### GET /attendance/view/<date_str>
指定日の勤怠記録の詳細を表示します（ログイン必須）。

**パスメータ:**
- `date_str`: 日付文字列 (YYYY-MM-DD形式)

### 社員管理（課長のみ）

#### GET /employees
社員一覧を表示します（ログイン必須・課長権限必須）。

#### GET /employees/create
社員作成フォームを表示します（ログイン必須・課長権限必須）。

#### POST /employees/create
社員を作成します（ログイン必須・課長権限必須）。

**リクエストパラメータ:**
- `email`: メールアドレス
- `password`: パスワード
- `name`: 氏名
- `role`: 権限（employee または manager）

#### GET /employees/edit/<employee_id>
社員編集フォームを表示します（ログイン必須・課長権限必須）。

**パスパラメータ:**
- `employee_id`: 社員ID

#### POST /employees/edit/<employee_id>
社員情報を更新します（ログイン必須・課長権限必須）。

**リクエストパラメータ:**
- `email`: メールアドレス
- `password`: パスワード（変更する場合のみ、省略可）
- `name`: 氏名
- `role`: 権限（employee または manager）

#### POST /employees/delete/<employee_id>
社員を削除します（ログイン必須・課長権限必須）。

**パスメータ:**
- `employee_id`: 社員ID

### レポート（課長のみ）

#### GET /report/monthly
月次レポートを表示します（ログイン必須・課長権限必須）。

**クエリパラメータ:**
- `year`: 年（省略可、デフォルトは今月）
- `month`: 月（省略可、デフォルトは今月）

### システム管理

#### GET /db/status
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
docker compose exec web python -m pytest tests/ui/test_login.py -v

# テスト結果を詳細に表示
docker compose exec web python -m pytest tests/ui/ -v -s
```

### 単体テストの実行

```bash
# すべての単体テストを実行
docker compose exec web python -m pytest tests/unit/ -v

# 特定のテストファイルを実行
docker compose exec web python -m pytest tests/unit/test_app.py -v
```

### 結合テストの実行

```bash
# 結合テストを実行
docker compose exec web python -m pytest tests/integration/ -v
```

### すべてのテストの実行

```bash
# すべてのテストを実行
docker compose exec web python -m pytest tests/ -v
```

## 環境変数

### webサービス

- `FLASK_ENV`: Flask環境（デフォルト: development）
- `FLASK_APP`: Flaskアプリケーションファイル（デフォルト: app.py）
- `SECRET_KEY`: Flaskセッション用のシークレットキー（デフォルト: dev-secret-key-change-in-production）
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

### データベースの初期化エラー

```bash
# データベースボリュームを削除して再初期化
docker compose down -v
docker compose up -d --build
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

### 実行環境

- プログラムの実行は必ずDockerコンテナ上で行います
- ローカル環境での直接実行は避けてください

### テストと動作確認

- 製造したら必ずテストを作成して動作確認をしてください
- テストコードは適切なテストフレームワークを使用して記述してください

### バージョン管理

- コミット及びプッシュ時のコメントは日本語で記述してください

### 新しいテストの追加

新しいUIテストを追加する場合は、`tests/ui/` ディレクトリに `test_*.py` という形式でファイルを作成し、`BaseSeleniumTest` クラスを継承してください。

新しい単体テストを追加する場合は、`tests/unit/` ディレクトリに `test_*.py` という形式でファイルを作成してください。

### ソースコードの変更

`src/app.py` を編集すると、ボリュームマウントにより変更が自動的に反映されます。Flaskアプリケーションの再起動は不要です（開発モードの場合）。

### 設計書の参照

設計書については、`docs/設計書一覧.md` ファイルを参照してください。

## 今後の拡張予定

### インフラ・開発環境
- データベースマイグレーション設定
- 環境変数ファイル（.env）の追加
- requirements.txtによる依存関係管理

### 機能拡張（将来の拡張予定）
- 残業時間の自動計算機能
- 年次レポート機能
- 給与計算システムとの連携
- 申請・承認機能（有休申請、残業申請など）
- 勤怠データの承認・修正機能（管理者による）

## ライセンス

このプロジェクトのライセンス情報をここに記載してください。

## 貢献

プルリクエストやイシューの報告を歓迎します。貢献する前に、コーディングスタイルガイドラインを確認してください。

## 更新履歴

- **2024-10-31**: プロジェクトの初期作成
  - Flask、MySQL、phpMyAdmin、Seleniumの統合
  - 勤怠管理システムの基本機能実装
  - 認証・権限管理機能の実装
  - UIテストの実装
