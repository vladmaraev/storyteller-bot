import os
import random
import nltk
import uuid
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

MONGO_URL = os.environ.get('MONGODB_URI')
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017/apiai";

app = Flask(__name__)
app.debug = True
app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)

def read_stories():
    with open('data/stories.csv') as f:
        stories_raw = f.readlines()
    return stories_raw

@app.route('/')
def index():
    #new_story('123')
    #print(mongo.db.sessions.find_one({'session_id':'123'}))
    return 'Yo, it is working!'

@app.route('/next')
def nextl():
    #next_line('123')
    #print(mongo.db.sessions.find_one({'session_id':'123'}))
    return 'Yo, it is working!'

def new_story(session_id):
    stories_raw = read_stories()
    session = mongo.db.sessions.find_one({'session_id':session_id})
    if session:
        stories_indexes = session['stories_indexes']
    else:
        stories_indexes = []
    allowed_indexes = [x for x in range(len(stories_raw)) if x not in stories_indexes]
    if not allowed_indexes:
        stories_indexes = []
        allowed_indexes = range(len(stories_raw))
    random_index = random.choice(allowed_indexes)
    stories_indexes.append(random_index)
    story = stories_raw[random_index]
    lines = nltk.sent_tokenize(story)
    mongo.db.sessions.update({'session_id': session_id},
                             {'session_id': session_id,
                              'stories_indexes': stories_indexes,
                              'next_line': 0,
                              'story': {'id': random_index,
                                        'lines': lines}},
                             upsert=True)

def next_line(session_id):
    session = mongo.db.sessions.find_one({'session_id': session_id})
    n = session['next_line']
    if n < len(session['story']['lines']):
        line = session['story']['lines'][n]
        mongo.db.sessions.update({'session_id': session_id},
                                 {'$inc': {'next_line': 1}},
                                 upsert=True)
        return line
    else:
        return 'END_OF_STORY' 


def send_reply(text):
    return {"speech": text,
            "displayText": text,
            "data": { "facebook" : facebook_reply(text),
                      "telegram" : telegram_reply(text)}}

    
def facebook_reply(text):
    return {"text": text,
            "quick_replies": [{"content_type": "text", "title": "•••", "payload": "GROUND"},
                              {"content_type": "text", "title": "?", "payload": "CONFUSION",
                               "image_url":"https://emojipedia-us.s3.amazonaws.com/thumbs/240/apple/96/thinking-face_1f914.png"},
                              {"content_type": "text", "title": "👍", "payload": "THUMBUP"},
                              {"content_type": "text", "title": "😆", "payload": "LAUGH"},
                              {"content_type": "text", "title": "😊", "payload": "SMILE"},
                              {"content_type": "text", "title": "😮", "payload": "SURPRISE"},
                              {"content_type": "text", "title": "😢", "payload": "SAD"},
                              {"content_type": "text", "title": "😡", "payload": "ANGER"},
                              {"content_type": "text", "title": "😨", "payload": "FEAR"}]}

def telegram_reply(text):
    return {"text": text,
            "reply_markup": {"inline_keyboard": [[{"text": "•••", "callback_data": "GROUND"}],
                                                 [{"text": "🤔", "callback_data": "CONFUSION"}],
                                                 [{"text": "👍", "callback_data": "THUMBUP"}],
                                                 [{"text": "😆", "callback_data": "LAUGH"}],
                                                 [{"text": "😊", "callback_data": "SMILE"}],
                                                 [{"text": "😮", "callback_data": "SURPRISE"}],
                                                 [{"text": "😢", "callback_data": "SAD"}],
                                                 [{"text": "😡", "callback_data": "ANGER"}],
                                                 [{"text": "😨", "callback_data": "FEAR"}]]}}
    
@app.route('/apiai', methods=['POST'])
def apiai():
    print(request.json)
    session_id = request.json['sessionId']
    if request.json['result']['action'] == 'newStory':
        new_story(session_id)
        line = next_line(session_id)
        return jsonify(send_reply(line))
    elif request.json['result']['action'] == 'nextLine':
        line = next_line(session_id)
        if line != 'END_OF_STORY':
            return jsonify(send_reply(line))
        else:
            reply = send_reply("That's it. How do you like a story?")
            reply["followupEvent"] = {"name": "newStoryEvent"}
            return jsonify(reply)

if __name__ == "__main__":
    app.run()
