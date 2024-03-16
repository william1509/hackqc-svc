import base64
import json
import traceback
import uuid
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request, send_file
import sqlalchemy
from werkzeug.utils import secure_filename
from cohere_client import CohereClient
from database import init_db, conn, users, plants, user_plants
from os import environ
from pathlib import Path
from sqlalchemy import select

from exception import APIError
from plant_client import PlantClient

app = Flask(__name__)

load_dotenv(override=True)

app.config['PLANT_ID_API_KEY'] = environ.get('PLANT_ID_API_KEY')
app.config['UPLOAD_FOLDER'] = environ.get('UPLOAD_FOLDER')
app.config['ALLOWED_EXTENSIONS'] = environ.get('ALLOWED_EXTENSIONS')
app.config['INITIAL_DATA'] = environ.get('INITIAL_DATA')
app.config['COHERE_API_KEY'] = environ.get('COHERE_API_KEY')
plant_client = PlantClient(app.config['PLANT_ID_API_KEY'])

cohere = CohereClient(app.config['COHERE_API_KEY'])

@app.route("/reference/<img>", methods=["GET"])
def reference(img: str):
    p = Path(f"../images/reference/{img}")
    return send_file(p, mimetype='image/jpg')

@app.route("/signup", methods=["GET"])
def signup():
    username = request.args.get('user')
    conn.execute(users.insert(), {
        "name": username
    })
    conn.commit()

    rows = conn.execute(users.select().where(users.c.name == username)).fetchone()
    if rows is None:
        raise APIError(403, "User doesn't exist")
    
    return jsonify(rows._asdict())

@app.route("/authenticate", methods=["GET"])
def authenticate():
    user = request.args.get('user')
    rows = conn.execute(users.select().where(users.c.name == user)).fetchone()
    if rows is None:
        raise APIError(403, "User doesn't exist")
    
    return jsonify(rows._asdict())
    
@app.route("/identify", methods=["POST"])
def identify():
    user = request.form.get("user")
    long = request.form.get("long")
    lat = request.form.get("lat")
    file = request.form.get("file")
    local_file_path = f"{app.config['UPLOAD_FOLDER']}/{uuid.uuid1()}"

    with open(local_file_path, "wb") as fh:
        fh.write(base64.decodebytes(str.encode(file)))

    suggestion = plant_client.identify(local_file_path)
    row = conn.execute(select(plants.c.name).where(plants.c.name == suggestion.name)).fetchone()
    print(row)
    if (row[0] is None):
        raise APIError(400, "No plant detected")
    cursor = conn.execute(user_plants.insert(), {
        "user": user,
        "plant": row[0],
        "img_path": f"{app.config['UPLOAD_FOLDER']}/{local_file_path}",
        "long": long,
        "lat": lat
    })
    conn.commit()

    rows = conn.execute(user_plants.select().where(user_plants.c.user == user).where(user_plants.c.plant == row[0])).fetchone()

    return jsonify(rows._asdict())

@app.route("/userplants", methods=["GET"])
def get_plants_for_user():
    user = request.args.get('user')
    plant = request.args.get('plant')
    stm = user_plants.select()
    if user:
        stm = stm.where(user_plants.c.user == user)
    if plant:
        stm = stm.where(user_plants.c.plant == plant)
    cursor = conn.execute(stm).fetchall()
    response = [row._asdict() for row in cursor]

    return jsonify(response)

@app.route("/allplants", methods=["GET"])
def get_all_plants():
    cursor = conn.execute(plants.select()).fetchall()
    response = [row._asdict() for row in cursor]

    return jsonify(response)

@app.route("/ask", methods=["POST"])
def ask():
    plant = request.args.get('plant')
    if plant is None:
        raise APIError(400, "No plant code provided")
    prompt = request.form.get("prompt")
    if prompt is None:
        raise APIError(400, "No prompt provided")
    response = cohere.ask(plant, prompt)
    return jsonify(response)

@app.teardown_appcontext
def shutdown_session(exception=None):
    pass


"""
Error handling
"""
@app.errorhandler(APIError)
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
    app.logger.error(f"Unknown Exception: {str(err)}")
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
    
    app.run('0.0.0.0', threaded=True)