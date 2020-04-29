from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from firebase.firestore.main import FireStore
fireStore = FireStore('./firebase/firestore/cred.json')

from analysis.main import Analysis
analysis = Analysis(dir='./analysis/dic/mecab-ipadic-neologd')

@app.route('/test', methods=['GET'])
def get_test():
  return 'Hello! I am Flask server!!'
