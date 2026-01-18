# Quiz_App

クイズアプリケーション - Flaskベースのインタラクティブなクイズシステム

## 機能

- Excelファイルからクイズデータを読み込み
- ゲームパッド対応
- オーバーレイ表示機能
- リアルタイムでのクイズ表示

## 必要要件

- Python 3.x
- Flask
- pandas
- openpyxl

## セットアップ

1. リポジトリをクローン:
```bash
git clone https://github.com/kenzo-x/Quiz_App.git
cd Quiz_App
```

2. 依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

## 実行方法

```bash
python app.py
```

アプリケーションが起動したら、ブラウザで http://localhost:5000 にアクセスしてください。

## Windows向けexe化（PyInstaller）

### 前提
- Windows環境
- Python 3.x

### 手順

1. 仮想環境の作成と有効化:
```bat
python -m venv .venv
.venv\Scripts\activate
```

2. 依存パッケージのインストール:
```bat
pip install -r requirements.txt
pip install pyinstaller
```

3. exeビルド:
```bat
pyinstaller --noconsole --add-data "templates;templates" --add-data "static;static" --add-data "data;data" app.py
```

4. 起動:
`dist\app\app.exe` を起動し、ブラウザで http://localhost:5200 にアクセスしてください。

### 補足
- `dist\app\data` にあるExcelが優先的に読み込まれます。
- 単一exeにしたい場合は `--onefile` を追加できますが、`data` の差し替え運用なら one-dir の方が扱いやすいです。

## プロジェクト構成

```
Quiz_App/
├── app.py                 # メインアプリケーション
├── quiz_engine.py         # クイズエンジン
├── requirements.txt       # 依存パッケージ
├── data/                  # クイズデータ（Excel形式）
│   ├── quiz.xlsx
│   └── sony_prospectus_quiz.xlsx
├── static/               # 静的ファイル
│   ├── css/
│   └── js/
└── templates/            # HTMLテンプレート
    ├── quiz.html
    └── overlay.html
```

## 使用方法

1. クイズデータは `data/` フォルダ内のExcelファイルに格納
2. アプリケーションを起動
3. ブラウザでクイズにアクセス
4. ゲームパッドまたはキーボードで操作
