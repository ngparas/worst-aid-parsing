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

@app.route('/classifier')
def classify_text():
    query = request.args.get('query')
    if any([i in query for i in ['next', 'forward', 'continue', 'go on', 'keep going']]):
        return json.dumps({'textClass': 'nav',
                           'value': 'next'})
    elif any([i in query for i in ['previous', 'back']]):
        return json.dumps({'textClass': 'nav',
                           'value': 'prev'})
    elif any([i in query for i in ['repeat']]):
        return json.dumps({'textClass': 'nav',
                           'value': 'stay'})
    elif any([i in query for i in ['yes', 'yeah', 'yah', 'sure', 'great', 'okay', 'yup']]):
        return json.dumps({'textClass': 'answer',
                           'value': True})
    elif any([i in query for i in ['no', 'nope', 'nah']]):
        return json.dumps({'textClass': 'answer',
                           'value': False})
    else:
        return json.dumps({'textClass': 'question',
                           'value': True})


if __name__ == '__main__':
    app.run()
