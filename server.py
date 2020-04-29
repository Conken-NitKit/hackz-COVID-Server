from flask import Flask, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

from firebase.firestore.main import FireStore
firestore = FireStore('./firebase/firestore/cred.json')

from analysis.main import Analysis
analysis = Analysis(dir='./analysis/dic/mecab-ipadic-neologd')

@app.route('/test', methods=['GET'])
def get_test():
  return 'Hello! I am Flask server!!'

# ユーザーID -> ユーザー情報
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id: str) -> {}:
  return firestore.id_to_data(collection='Users', id=user_id)

# ミーティングID -> ミーティング情報
@app.route('/meetings/<meeting_id>', methods=['GET'])
def get_meeting(meeting_id: str) -> {}:
  return firestore.id_to_data(collection='Meetings', id=meeting_id)

# ミーティングID -> 参加しているユーザーの名前・ID情報
@app.route('/meetings/users/<meeting_id>', methods=['GET'])
def get_joining_users(meeting_id: str) -> {}:
  meeting_data = firestore.id_to_data(collection='Meetings', id=meeting_id)
  return {
    'owner': meeting_data['owner'],
    'members': meeting_data['members']
  }

# ユーザーの新規登録
# ユーザー名 -> ユーザーID
@app.route('/users/init', methods=['POST'])
def init_user():
  req = json.loads(request.get_data().decode())
  name = req['name']

  return firestore.init_user(name=name)

# ミーティングの新規作成
@app.route('/meetings/init', methods=['POST'])
def init_meeting() -> {}:
  req = json.loads(request.get_data().decode())
  title = req['title']
  owner_id = req['owner_id']

  return firestore.init_meeting(title=title, owner_id=owner_id)

# ミーティングへのユーザーの追加
@app.route('/meetings/add_user', methods=['POST'])
def add_user() -> str:
  req = json.loads(request.get_data().decode())
  meeting_id = req['meeting_id']
  user_id = req['user_id']

  return firestore.add_user(meeting_id=meeting_id, user_id=user_id)

# ミーティングへの議事録の追加
@app.route('/meetings/add_record', methods=['POST'])
def add_record() -> None:
  req = json.loads(request.get_data().decode())
  meeting_id = req['meeting_id']
  user_id = req['user_id']
  record_data = req['record_data']

  firestore.add_record(meeting_id=meeting_id, user_id=user_id, record_data=record_data)

  return 'OK'

# ミーティングへのブラックリストの追加
@app.route('/meetings/add_black_list', methods=['POST'])
def add_black_list() -> None:
  req = json.loads(request.get_data().decode())
  meeting_id = req['meeting_id']
  black_words = req['black_words']

  firestore.add_black_list(meeting_id=meeting_id, black_words=black_words)

  return 'OK'

# ミーティングの終了命令
# ミーティングID -> キーワード更新後のミーティング情報
@app.route('/meetings/finish', methods=['POST'])
def finish_meeting() -> {}:

  req = json.loads(request.get_data().decode())
  meeting_id = req['meeting_id']

  print(meeting_id)

  meeting_data = firestore.id_to_data(collection='Meetings', id=meeting_id)
  records_markdown = [record[1]['markdown'] for record in list(meeting_data['records'].items())]
  
  keywords=analysis.main(text_list=records_markdown)
  firestore.update_keywords(meeting_id=meeting_id, keywords=keywords)

  firestore.id_to_data(collection='Meetings', id=meeting_id)

  return 'OK'