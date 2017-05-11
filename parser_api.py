from flask import Flask
from flask import request
from flask import render_template
from fuzzywuzzy import process
import json

import redis

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/procedures')
def get_procedure():
    query = request.args.get('query')

    available_keys = [i.decode('utf-8').replace('-', ' ') for i in redis_client.keys()]
    target_key = process.extractOne(query, available_keys)[0].replace(' ', '-')
    return json.dumps({'key': target_key, 'graph': json.loads(redis_client.get(target_key).decode('utf-8'))})



if __name__ == '__main__':
    app.run()
