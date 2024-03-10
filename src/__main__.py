import json
import traceback
from flask import Flask, jsonify, make_response, request
import sqlalchemy
from werkzeug.utils import secure_filename
from database import UserPlants, init_db, conn, users, plants
from os import environ

from plant_client import PlantClient
from exception import AuthError, SignUpError

app = Flask(__name__)
app.config['PLANT_ID_API_KEY'] = environ.get('PLANT_ID_API_KEY')
app.config['UPLOAD_FOLDER'] = environ.get('UPLOAD_FOLDER')
app.config['ALLOWED_EXTENSIONS'] = environ.get('ALLOWED_EXTENSIONS')
app.config['INITIAL_DATA'] = environ.get('INITIAL_DATA')
plant_client = PlantClient(app.config['PLANT_ID_API_KEY'])


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/signup", methods=["GET"])
def signup():
    username = request.args.get('username')
    conn.execute(users.insert(), {
        "name": username
    })
    return jsonify(True)

@app.route("/authenticate", methods=["GET"])
def authenticate():
    username = request.args.get('username')
    user = conn.execute(users.select().where(users.c.name == username).limit(1)).fetchall()
    return jsonify(user.count == 1)
    
@app.route("/identify", methods=["POST"])
def identify():
    username = request.args.get('username')
    file = request.files['file']
    local_file_path = f"{app.config['UPLOAD_FOLDER']}/{secure_filename(file.filename)}"

    # file.save(local_file_path)
    suggestion = plant_client.identify("images/user/plant.png")
    conn.execute(UserPlants.insert(), {
        "name": username
    })

    return jsonify(suggestion)

@app.route("/plants", methods=["GET"])
def get_plants():
    result = conn.execute(plants.select().where(plants.c.name == "Solidago canadensis")).fetchall()
    print(result)
    results = [tuple(row) for row in result]
    return jsonify(results)


@app.teardown_appcontext
def shutdown_session(exception=None):
    pass

@app.errorhandler(AuthError)
def handle_exception(err):
    """Return JSON instead of HTML for MyCustomError errors."""
    response = {
      "error": err.description, 
    }
    if len(err.args) > 0:
        response["message"] = err.args[0]
    return jsonify(response), err.code

@app.errorhandler(SignUpError)
def handle_exception(err):
    """Return JSON instead of HTML for MyCustomError errors."""
    response = {
      "error": err.description, 
    }
    if len(err.args) > 0:
        response["message"] = err.args[0]
    return jsonify(response), err.code

@app.errorhandler(sqlalchemy.exc.SQLAlchemyError)
def handle_exception(err):
    """Handle DB connection errors """
    response = {}
    if isinstance(err, sqlalchemy.exc.InternalError):
        response["message"] = "Unable to connect to DB"
    if isinstance(err, sqlalchemy.exc.IntegrityError):
        response["message"] = "Username already exists"
    app.logger.debug(''.join(traceback.format_exception(err)))
    return jsonify(response), 555

@app.errorhandler(500)
def handle_exception(err):
    """Return JSON instead of HTML for any other server error"""
    app.logger.error(f"Unknown Exception: {str(err)}")
    app.logger.debug(''.join(traceback.format_exception(err)))
    response = {"error": "Uncaught exception"}
    return jsonify(response), 500

if __name__ == '__main__':
    init_db(app.config['INITIAL_DATA'])
    
    app.run('0.0.0.0')