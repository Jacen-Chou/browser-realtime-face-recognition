import json
import os
from flask import Flask, request
from flask_cors import *

app = Flask(__name__)
CORS(app, supports_credentials=True)
FACE_DB_PATH = os.path.join(os.path.split(__file__)[0], 'src/descriptors/face-db.json')
update_lock = False


def load_face_db():
    with open(FACE_DB_PATH, 'r', encoding='UTF-8') as f:
        face_db = json.load(f)
    return face_db


def save_face_db(data):
    global update_lock
    if update_lock:
        raise Exception('Updating falied, face-db.json has been locked.')
    update_lock = True
    with open(FACE_DB_PATH, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False)
    update_lock = False


face_db = load_face_db()


@app.route('/', methods=['GET'])
def index():
    return 'browser-face-realtime-recognition json server has been started.'


@app.route('/api/face-db', methods=['GET', 'POST', 'PUT'])
def api_face_db():
    global face_db

    if request.method == 'GET':
        return json.dumps(face_db, ensure_ascii=False)

    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data.decode())
        face_db = data
        try:
            save_face_db(face_db)
            return json.dumps({'success': True}), 200
        except Exception as e:
            return json.dumps({'success': False, 'message': str(e)}), 400

    if request.method == 'PUT':
        data = request.get_data()
        print(data)
        data = json.loads(data.decode())
        print(data)
        if not len(data.keys()) == 1:
            return json.dumps({'success': False, 'message': 'Must have one key.'}), 400
        name = list(data.keys())[0]
        print(name)
        print(data[name]['descriptors'])
        if not (
                isinstance(data[name], object)
                and data[name].get('descriptors')
                and isinstance(data[name]['descriptors'], list)):
            return json.dumps({'success': False, 'message': 'Descriptors must be a array'}), 400
        if not face_db.get(name):
            face_db[name] = data[name]
        else:
            face_db[name]['descriptors'].extend(data[name]['descriptors'])
        save_face_db(face_db)
        return json.dumps({'success': True})


if __name__ == "__main__":
    app.run('0.0.0.0', 3001)
