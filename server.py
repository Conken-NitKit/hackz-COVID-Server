from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test', methods=['GET'])
def get_test():
  return 'Hello! I am Flask server!!'
