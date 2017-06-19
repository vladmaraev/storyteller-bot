import random
import nltk
import uuid
from flask import Flask, request, jsonify
app = Flask(__name__)

def read_stories():
    with open('data/stories.csv') as f:
        stories_raw = f.readlines()
    return stories_raw

@app.route('/')
def index():
    return 'Yo, it is working!'

def new_story(session_id):
    story = random.choice(stories_raw)
    lines = nltk.sent_tokenize(story)
    #session_id = str(uuid.uuid4()) 
    sessions[session_id] = {'session_id': session_id,
                            'story_id': "TBD",
                            'next_line': 0,
                            'lines':lines,
                            'reactions':[]}
    return session_id

def next_line(session_id):
    n = sessions[session_id]['next_line']
    if n < len(sessions[session_id]['lines']):
        line = sessions[session_id]['lines'][n]
        sessions[session_id]['next_line'] += 1
        return line
    else:
        return 'END_OF_STORY'

def facebook_reply(text):
    return {"speech": text,
            "displayText": text,
            "data": {
                "facebook": {
                    "text": text,
                    "quick_replies": [{"content_type": "text", "title": "•••", "payload": "GROUND"},
                                      {"content_type": "text", "title": "🙂", "payload": "SMILE"}]}}}
    
@app.route('/apiai', methods=['POST'])
def apiai():
    print(request.json)
    session_id = request.json['sessionId']
    if request.json['result']['action'] == 'newStory':
        new_story(session_id)
        line = next_line(session_id)
        return jsonify(facebook_reply(line))
    elif request.json['result']['action'] == 'nextLine':
        line = next_line(session_id)
        if line != 'END_OF_STORY':
            return jsonify(facebook_reply(line))
        else:
            reply = facebook_reply("That's it. How do you like a story?")
            reply["followupEvent"] = {"name": "newStoryEvent"}
            return jsonify(reply)
    
if __name__ == "__main__":
    stories_raw = read_stories()
    sessions = {}
    print("all is set")
    app.run()
