from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Yo, it is working!'

@app.route('/new')
def new_story():
    return 'here is the story'

    
if __name__ == "__main__":
	app.run()

