# gpt-playground

[独自のデータに対してchatgpt回答を得る](https://qiita.com/YoshitakaOkada/items/67de6a17b91a676d1112)

## 参考

[話題の ChatGPT + LangChain で、膨大な PDF ドキュメントの内容を爆速で把握する](https://qiita.com/hiroki_okuhata_int/items/7102bab7d96eb2574e7d)

## ライブラリをインストールする

```console
pip install -r requirements.txt

-- ※開発時 現在のライブラリの状態でrequirementsを書き出す
pip freeze > requirements.txt
```

## オペ

pk=1のユーザーを使用するので createsuperuser でユーザーを作ってから runserver してください

```
python manage.py makemigrations retrieval_qa_with_source line_qa_with_gpt_and_dalle
python manage.py migrate
python manage.py collectstatic

python manage.py createsuperuser
python manage.py runserver
```

## geoService

```
pip install rasterio affine
```

## google drive

### 前提条件

1. Google Drive APIの有効化
   Google Cloud ConsoleでGoogle Drive APIを有効にします。

2. 認証情報の設定
   OAuth2認証を使用するために、認証情報（credentials.json）をダウンロードしてプロジェクトに配置します。

3. 必要なライブラリをインストール
   必要なライブラリをインストールします。
   ```
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

### 実行手順

`credentials.json` を準備。
フォルダID（Google Drive URLのhttps://drive.google.com/drive/folders/<folder_id>部分）を指定。
スクリプトを実行。
