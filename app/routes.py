from app import app
#Contains the different URLs of the bank webapp

@app.route('/')
@app.route('/index')
def index():
    return "Hello World"