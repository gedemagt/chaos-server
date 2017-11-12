from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

def get_sql_position():
    path = os.path.join(os.path.dirname(__file__), 'sql_path.txt')
    with open(path) as f:
        return f.readline()

app = Flask(__name__, static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = get_sql_position()
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
    coordinates = db.Column(db.String, default="{}")
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    gym = db.Column(db.Integer, db.ForeignKey('gym.id'))
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
    author = request.json['author']
    gym = request.json['gym']
    date = request.json['date']
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    db.session.add(Rute(uuid=uuid, name=name, coordinates="[]", author=author, gym=gym, date=date))
    db.session.commit()

    return str(db.session.query(Rute).order_by(Rute.id.desc()).first().id)


@app.route('/add_image/<string:uuid>', methods=['POST'])
def upload_image(uuid):
    f = request.files['file']
    filename = "{}.jpg".format(db.session.query(Rute).filter_by(uuid=uuid).first().id)
    f.save(os.path.join('static', filename))

    return "Succes"


@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    coordinates = request.json['coordinates']
    uuid = request.json['uuid']

    rute = db.session.query(Rute).filter_by(uuid=uuid).first()
    rute.coordinates = coordinates
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


@app.route('/get_rutes', methods=['GET'])
def get_rutes():
    r = {rute.id: {"author": rute.author,
                   "date": str(rute.date),
                   "coordinates": rute.coordinates,
                   "gym": rute.gym,
                   "name": rute.name,
                   "uuid": rute.uuid}
         for rute in db.session.query(Rute)}

    return jsonify(r), 200


@app.route('/download/<string:uuid>', methods=['GET','0;256;0c0;256;0cPOST'])
def download_image(uuid):
    filename = "{}.jpg".format(db.session.query(Rute).filter_by(uuid=uuid).first().id)
    if not os.path.exists(os.path.join('static', filename)):
        return "No file", 204
    return send_from_directory('static', filename)

@app.route('/delete/<string:uuid>', methods=['POST'])
def delete_image(uuid):
    rute = db.session.query(Rute).filter_by(uuid=uuid).first()
    db.session.delete(rute)
    db.session.commit()
    if os.path.exists(os.path.join('static', rute.id + ".jpg")):
        os.remove(os.path.join('static', rute.id + ".jpg"))
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


@app.route('/get_gym/<string:uuid>', methods=['POST'])
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
                   "uuid": user.uuid}
         for user in db.session.query(User)}

    return jsonify(r), 200


@app.route('/get_user/<string:uuid>', methods=['POST'])
def get_user(uuid):

    user = db.session.query(User).filter_by(uuid=uuid).first()

    r = {user.uuid: {"gym": user.gym,
                   "date": str(user.date),
                   "name": user.name,
                   "email": user.email}}

    return jsonify(r), 200


# @app.route('/get_comments/<string:uuid>')
# def get_comments(uuid):
#     r = {comment.id: {"text": comment.text,
#                       "date": str(comment.date),
#                       "author": comment.author,
#                       "rute": uuid}
#          for comment in db.session.query(Comment).filter_by(rute=uuid)}
#
#     return jsonify(r), 200


# @app.route('/get_ratings/<string:uuid>')
# def get_ratings(uuid):
#     r = {rating.uuid: {"rating": rating.rating,
#                       "date": str(rating.date),
#                       "author": rating.author,
#                       "rute": uuid}
#          for rating in db.session.query(Rating).filter_by(rute=uuid)}
#
#     return jsonify(r), 200


if __name__ == "__main__":

    import sys
    if "db" in sys.argv:
        print("Creates database")
        db.create_all()
        db.session.add(Gym(uuid="uuid1", name="ÅK", lat=0.0, lon=0.0))
        db.session.add(User(uuid="uuid2", name="Erik", password="pass", email="erik@gmail.com", gym=1))
        db.session.commit()
    else:
        app.run(debug=True)
