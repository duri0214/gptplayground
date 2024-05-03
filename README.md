# gpt-playground
[独自のデータに対してchatgpt回答を得る](https://qiita.com/YoshitakaOkada/items/67de6a17b91a676d1112)

## 参考
[話題の ChatGPT + LangChain で、膨大な PDF ドキュメントの内容を爆速で把握する](https://qiita.com/hiroki_okuhata_int/items/7102bab7d96eb2574e7d)

## オペ
```
python manage.py makemigrations retrieval_qa_with_source
python manage.py migrate
python manage.py collectstatic

python manage.py createsuperuser
python manage.py runserver
```
