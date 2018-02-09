from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


def get_sql_position():
    path = os.path.join(os.path.dirname(__file__), 'sql_path.txt')
    if not os.path.exists(path):
        raise ValueError("No 'sql_path.txt' found! Please place a sql_path.txt in the same directory as main.py"
                         "with one line: The path to the database!")
    with open(path) as f:
        return f.readline()


app = Flask(__name__, static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + get_sql_position()
db = SQLAlchemy(app)


class Gym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    uuid = db.Column(db.String)
    lat = db.Column(db.String)
    lon = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    uuid = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    gym = db.Column(db.Integer, db.ForeignKey('gym.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Rute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    uuid = db.Column(db.String)
    image = db.Column(db.String)
    coordinates = db.Column(db.String, default="{}")
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    gym = db.Column(db.Integer, db.ForeignKey('gym.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    edit = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.String, default="NO_GRADE")

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String)
    url = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    uuid = db.Column(db.String)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    rute = db.Column(db.Integer, db.ForeignKey('rute.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.String)
    uuid = db.Column(db.String)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    rute = db.Column(db.Integer, db.ForeignKey('rute.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/', methods=['GET'])
def index():
    return 'Hello'


@app.route('/add_rute', methods=['POST'])
def upload():

    name = request.json['name']
    uuid = request.json['uuid']
    image = request.json['image']
    author = request.json['author']
    gym = request.json['gym']
    date = request.json['date']
    edit = request.json['edit']
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    edit = datetime.strptime(edit, '%Y-%m-%d %H:%M:%S')
    grade = request.json['grade'] if 'grade' in request.json else 'NO_GRADE'

    db.session.add(Rute(uuid=uuid, name=name, coordinates="[]", author=author, gym=gym, date=date, edit=edit, image=image, grade=grade))
    db.session.commit()

    return str(db.session.query(Rute).order_by(Rute.id.desc()).first().id)


@app.route('/add_image/<string:uuid>', methods=['POST'])
def upload_image(uuid):
    f = request.files['file']
    filename = os.path.join('static', "{}.jpg".format(uuid))
    f.save(filename)
    db.session.add(Image(uuid=uuid, url=filename))
    db.session.commit()
    return "Succes"


@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():

    uuid = request.json['uuid']

    coordinates = request.json['coordinates']

    edit = request.json['edit']
    edit = datetime.strptime(edit, '%Y-%m-%d %H:%M:%S')

    rute = db.session.query(Rute).filter_by(uuid=uuid).first()
    rute.coordinates = coordinates
    if "name" in request.json:
        rute.name = request.json["name"]
    if "gym" in request.json:
        rute.gym = request.json["gym"]
    if 'grade' in request.json:
        rute.grade = request.json['grade']
    rute.edit = edit
    db.session.commit()
    return "Succes"


@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    gym = request.json['gym']
    uuid = request.json['uuid']

    db.session.add(User(uuid=uuid, name=username, password=password, email=email, gym=gym))
    db.session.commit()
    return "Succes"


@app.route('/add_gym', methods=['POST'])
def add_gym():
    name = request.json['name']
    lat = request.json['lat']
    lon = request.json['lon']
    uuid = request.json['uuid']

    db.session.add(Gym(uuid=uuid, name=name, lat=lat, lon=lon))
    db.session.commit()
    return "Succes"


@app.route('/get_rutes', methods=['GET','POST'])
def get_rutes():
    last_sync = request.json['last_sync']

    r = {rute.id: {"author": rute.author,
                   "grade": rute.grade,
                   "date": str(rute.date),
                   "edit": str(rute.edit),
                   "coordinates": rute.coordinates,
                   "gym": rute.gym,
                   "name": rute.name,
                   "image": rute.image,
                   "uuid": rute.uuid}
         for rute in db.session.query(Rute).filter(Rute.edit > last_sync)}

    return jsonify(r), 200


@app.route('/download/<string:uuid>', methods=['GET', 'POST'])
def download_image(uuid):

    url = db.session.query(Image).filter_by(uuid=uuid).first().url
    if not os.path.exists(url):
        return "No file", 204
    return send_from_directory('static', os.path.relpath(url, 'static'))


@app.route('/delete/<string:uuid>', methods=['POST'])
def delete_image(uuid):
    rute = db.session.query(Rute).filter_by(uuid=uuid).first()
    if rute is not None:
        db.session.delete(rute)
    db.session.commit()

    return "Succes", 200


@app.route('/get_gyms', methods=['GET'])
def get_gyms():
    r = {gym.id: {"lat": gym.lat,
                  "date": str(gym.date),
                  "lon": gym.lon,
                  "name": gym.name,
                  "uuid": gym.uuid}
         for gym in db.session.query(Gym)}

    return jsonify(r), 200


@app.route('/get_gym/<string:uuid>', methods=['GET'])
def get_gym(uuid):

    gym = db.session.query(Gym).filter_by(uuid=uuid).first()

    r = {uuid: {"lat": gym.lat,
                  "date": str(gym.date),
                  "lon": gym.lon,
                  "name": gym.name,
                  "uuid": gym.uuid}}
    return jsonify(r), 200


@app.route('/get_users', methods=['GET'])
def get_users():
    r = {user.id: {"gym": user.gym,
                   "date": str(user.date),
                   "name": user.name,
                   "email": user.email,
                   "password":   user.password,
                   "uuid": user.uuid}
         for user in db.session.query(User)}

    return jsonify(r), 200


@app.route('/get_user/<string:uuid>', methods=['GET'])
def get_user(uuid):

    user = db.session.query(User).filter_by(uuid=uuid).first()

    r = {user.id: {"gym": user.gym,
                   "date": str(user.date),
                   "name": user.name,
                     "password": user.password,
                     "uuid": user.uuid,
                   "email": user.email}}

    print(r)
    return jsonify(r), 200


if __name__ == "__main__":

    import sys
    if "db" in sys.argv or not os.path.exists(get_sql_position()):
        print("Creates database")
        db.create_all()
        db.session.add(Gym(uuid="UnknowGym", name="Unknown Gym", lat=1, lon=1))
        db.session.add(User(uuid="admin", name="admin", password="admin", email="", gym="UnknowGym"))
        db.session.commit()


    app.run(debug=True)
