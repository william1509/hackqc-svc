import json
from flask import Flask, request
from werkzeug.utils import secure_filename
from database import init_db, conn, users
from repositories.user_repository import UserRepository
from models import User

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/signup", methods=["GET"])
def signup():
    try:
        username = request.args.get('username')
        conn.execute(users.insert(), {
            "name": username
        })
        return json.dumps(username)
    except Exception as e:
        print(e)
        return None

@app.route("/authenticate", methods=["GET"])
def authenticate():
    username = request.args.get('username')
    user = conn.execute(users.select().where(users.c.name == username).limit(1)).fetchall()
    return user.count == 1
    
@app.route("/identify", methods=["POST"])
def identify():
    pass
    

@app.teardown_appcontext
def shutdown_session(exception=None):
    pass

if __name__ == '__main__':
    init_db()
    
    app.run('0.0.0.0')