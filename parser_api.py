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

    next_file = open('next_phrases.txt')
    prev_file = open('prev_phrases.txt')
    repeat_file = open('repeat_phrases.txt')
    yes_file = open('yes_phrases.txt')
    no_file = open('no_phrases.txt')


    if any([i.strip() in query.lower() for i in next_file]):
        return json.dumps({'textClass': 'nav',
                           'value': 'next'})
    elif any([i.strip() in query.lower() for i in prev_file]):
        return json.dumps({'textClass': 'nav',
                           'value': 'prev'})
    elif any([i.strip() in query.lower() for i in repeat_file]):
        return json.dumps({'textClass': 'nav',
                           'value': 'stay'})
    elif any([i.strip() in query.lower() for i in no_file]):
        return json.dumps({'textClass': 'answer',
                           'value': False})
    elif any([i.strip() in query.lower() for i in yes_file]):
        return json.dumps({'textClass': 'answer',
                           'value': True})
    else:
        return json.dumps({'textClass': 'question',
                           'value': True})


if __name__ == '__main__':
    app.run()
