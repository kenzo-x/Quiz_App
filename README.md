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
