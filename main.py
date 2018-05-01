from flask import request, jsonify, send_from_directory, abort
from datetime import datetime
import os
from flask_login import UserMixin, login_user, login_required, logout_user
import bcrypt
from server import db, app, login_manager, get_sql_position
from competition import competition
from random import randint

class Gym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    uuid = db.Column(db.String)
    lat = db.Column(db.String)
    lon = db.Column(db.String)
    admin = db.Column(db.String)
    sectors = db.Column(db.String)
    tags = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    edit = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer, default=0)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    uuid = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    role = db.Column(db.String)
    gym = db.Column(db.Integer, db.ForeignKey('gym.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    edit = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer, default=0)


class Rute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    uuid = db.Column(db.String)
    image = db.Column(db.String)
    coordinates = db.Column(db.String, default="{}")
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    gym = db.Column(db.Integer, db.ForeignKey('gym.id'))
    sector = db.Column(db.String)
    tag = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    edit = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.String, default="NO_GRADE")
    status = db.Column(db.Integer, default=0)


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


class UserClass(UserMixin):

    def __init__(self, uuid):
        self.uuid = uuid

    def get_id(self):
        return self.uuid


@login_manager.user_loader
def load_user(user_id):
    user = db.session.query(User).filter_by(name=user_id).first()
    if user is None:
        return None
    return UserClass(user_id)


@app.route('/', methods=['GET'])
def index():
    with open("privacy.html") as f:
        return f.read()
    return "JOHN"

@app.route('/privacy', methods=['GET', 'POST'])
def privacy():
    return app.send_static_file("privacy.html")

@app.route('/add_rute', methods=['POST'])
@login_required
def upload():
    uuid = request.json['uuid']
    if db.session.query(Rute).filter_by(uuid=uuid).first() is not None:
        abort(400)

    name = request.json['name']
    image = request.json['image']
    author = request.json['author']
    sector = request.json['sector']
    gym = request.json['gym']
    date = request.json['date']
    edit = request.json['edit']
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    edit = datetime.strptime(edit, '%Y-%m-%d %H:%M:%S')
    grade = request.json['grade'] if 'grade' in request.json else 'NO_GRADE'
    tag = request.json['tag'] if 'tag' in request.json else ''

    db.session.add(Rute(uuid=uuid, name=name, coordinates="[]", author=author, sector=sector, date=date, edit=edit, image=image, grade=grade, gym=gym, tag=tag))
    db.session.commit()

    return str(db.session.query(Rute).order_by(Rute.id.desc()).first().id)


@app.route('/add_image/<string:uuid>', methods=['POST'])
@login_required
def upload_image(uuid):
    f = request.files['file']
    filename = os.path.join('static', "{}.jpg".format(uuid))
    if os._exists(filename):
        abort(400)
    f.save(filename)
    db.session.add(Image(uuid=uuid, url=filename))
    db.session.commit()
    return "Succes"


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    user = db.session.query(User).filter_by(name=username).first()
    if user is None:
        abort(400)

    if not bcrypt.checkpw(password, user.password):
        abort(400)

    login_user(UserClass(username))

    return user.uuid


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return "Succes"



@app.route('/update_coordinates', methods=['POST'])
@login_required
def update_coordinates():

    uuid = request.json['uuid']

    coordinates = request.json['coordinates']
    edit = request.json['edit']
    edit = datetime.strptime(edit, '%Y-%m-%d %H:%M:%S')

    rute = db.session.query(Rute).filter_by(uuid=uuid).first()
    if rute is None:
        abort(400)
    rute.coordinates = coordinates
    if "name" in request.json:
        rute.name = request.json["name"]
    if "gym" in request.json:
        rute.gym = request.json["gym"]
    if 'grade' in request.json:
        rute.grade = request.json['grade']
    if 'sector' in request.json:
        rute.sector = request.json['sector']
    if 'tag' in request.json:
        rute.sector = request.json['tag']
    rute.edit = edit
    db.session.commit()
    return "Succes"


@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.json['username']
    password = request.json['password']
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    email = request.json['email']
    gym = request.json['gym']
    uuid = request.json['uuid']
    role = request.json.get('role', 'USER')
    if db.session.query(User).filter_by(name=username).first():
        abort(400)
    db.session.add(User(uuid=uuid, name=username, password=password, email=email, gym=gym, role=role))
    db.session.commit()
    return "Succes"


# @app.route('/add_sector', methods=['POST'])
# @login_required
# def add_sector():
#     name = request.json['name']
#     gym = request.json['gym']
#     uuid = request.json['uuid']
#     date = datetime.strptime(request.json['date'], '%Y-%m-%d %H:%M:%S')
#     if db.session.query(Sector).filter_by(gym=gym, name=name).first():
#         abort(400)
#     db.session.add(Sector(uuid=uuid, name=name, gym=gym, date=date))
#     db.session.commit()
#     return "Succes"

#
# @app.route('/get_sector/<string:uuid>', methods=['GET'])
# @login_required
# def get_sector(uuid):
#
#     sector = db.session.query(Sector).filter_by(uuid=uuid).first()
#     if sector is None:
#         abort(400)
#
#     r = {uuid: {
#                   "date": str(sector.date),
#                   "gym": sector.gym,
#                   "name": sector.name,
#                   "uuid": sector.uuid}}
#     return jsonify(r), 200


@app.route('/add_gym', methods=['POST'])
@login_required
def add_gym():
    name = request.json['name']
    lat = request.json['lat']
    lon = request.json['lon']
    uuid = request.json['uuid']

    if db.session.query(Gym).filter_by(name=name).first() is not None:
        abort(400)
    else:
        db.session.add(Gym(uuid=uuid, name=name, lat=lat, lon=lon))
        db.session.commit()
        return "Succes"


@app.route('/save_gym', methods=['POST'])
@login_required
def save_gym():
    name = request.json['name']
    lat = request.json['lat']
    lon = request.json['lon']
    uuid = request.json['uuid']
    sectors = request.json['sectors']
    tags = request.json['tags']
    edit = request.json['edit']

    gym = db.session.query(Gym).filter_by(uuid=uuid).first()
    if gym is None:
        abort(400)
    else:
        gym.name = name
        gym.lat = lat
        gym.lon = lon
        gym.sectors = sectors
        gym.tags = tags
        gym.edit = edit

        db.session.commit()
        return "Succes"


@app.route('/check_username/<string:name>', methods=['POST'])
def check_name(name):

    user = db.session.query(User).filter_by(name=name).first()
    if user is None:
        return "Success"
    else:
        abort(400)


@app.route('/get_rutes', methods=['GET','POST'])
@login_required
def get_rutes():
    last_sync = '1900-02-13 22:25:33'
    if request.json and 'last_sync' in request.json:
        last_sync = request.json.get('last_sync')

    r = {rute.id: {"author": rute.author,
                   "grade": rute.grade,
                   "date": str(rute.date),
                   "edit": str(rute.edit),
                   "coordinates": rute.coordinates,
                   "gym": rute.gym,
                   "sector": rute.sector,
                   "tag": rute.sector,
                   "name": rute.name,
                   "image": rute.image,
                   "uuid": rute.uuid,
                   "tag": rute.tag,
                   "status": rute.status}
         for rute in db.session.query(Rute).filter(Rute.edit > last_sync)}

    return jsonify(r), 200


@app.route('/download/<string:uuid>', methods=['GET', 'POST'])
@login_required
def download_image(uuid):

    img = db.session.query(Image).filter_by(uuid=uuid).first()
    if img is None:
        abort(400)
    if not os.path.exists(img.url):
        abort(400)
    return send_from_directory('static', os.path.relpath(img.url, 'static'))


@app.route('/delete/<string:uuid>', methods=['POST'])
@login_required
def delete_image(uuid):
    rute = db.session.query(Rute).filter_by(uuid=uuid).first()
    if rute is not None:
        rute.status = 1
        rute.edit = datetime.utcnow()
    db.session.commit()

    return "Succes", 200


@app.route('/delete_gym/<string:uuid>', methods=['POST'])
@login_required
def delete_gym(uuid):
    gym = db.session.query(Gym).filter_by(uuid=uuid).first()
    if gym is not None:
        gym.status = 1
        gym.edit = datetime.utcnow()
    db.session.commit()

    return "Succes", 200


@app.route('/delete_user/<string:uuid>', methods=['POST'])
@login_required
def delete_user(uuid):
    user = db.session.query(User).filter_by(uuid=uuid).first()
    if user is not None:
        user.status = 1
        user.edit = datetime.utcnow()
    db.session.commit()

    return "Succes", 200


@app.route('/check_gymname/<string:name>', methods=['POST'])
def check_gymname(name):

    gym = db.session.query(Gym).filter_by(name=name).first()
    if gym is None:
        return "Success"
    else:
        abort(400)


@app.route('/get_gyms', methods=['GET'])
def get_gyms():
    r = {gym.id: {"lat": gym.lat,
                  "date": str(gym.date),
                  "edit": str(gym.edit),
                  "status": gym.status,
                  "lon": gym.lon,
                  "name": gym.name,
                  "uuid": gym.uuid,
                  "tags": gym.tags,
                  "sectors": gym.sectors}
         for gym in db.session.query(Gym)}
    return jsonify(r), 200


@app.route('/get_gym/<string:uuid>', methods=['GET'])
def get_gym(uuid):

    gym = db.session.query(Gym).filter_by(uuid=uuid).first()

    r = {uuid: {"lat": gym.lat,
                  "date": str(gym.date),
                  "edit": str(gym.edit),
                  "status": gym.status,
                  "lon": gym.lon,
                  "name": gym.name,
                  "uuid": gym.uuid,
                  "tags": gym.tags,
                  "sectors": gym.sectors}}
    return jsonify(r), 200


@app.route('/get_users', methods=['GET'])
@login_required
def get_users():
    r = {user.id: {"gym": user.gym,
                   "date": str(user.date),
                   "name": user.name,
                   "email": user.email,
                   "password":   user.password,
                   "role": user.role,
                   "uuid": user.uuid}
         for user in db.session.query(User)}

    return jsonify(r), 200


@app.route('/get_user/<string:uuid>', methods=['GET'])
@login_required
def get_user(uuid):

    user = db.session.query(User).filter_by(uuid=uuid).first()

    r = {user.id: {"gym": user.gym,
                   "date": str(user.date),
                   "name": user.name,
                    "password": user.password,
                    "uuid": user.uuid,
                   "role": user.role,
                   "email": user.email}}

    return jsonify(r), 200


@app.route('/get_comp/<int:pin>', methods=['GET'])
def get_comp(pin):
    comp = db.session.query(competition.Competition).filter_by(pin=pin).first()
    if comp is None:
        abort(400)

    r = {"uuid": comp.uuid,
         "name": comp.name,
         "date": str(comp.date),
         "edit": str(comp.edit),
         "start": str(comp.start),
         "stop": str(comp.stop),
         "type": comp.type,
         "admins": comp.admins.split(","),
         "pin": comp.pin,
         "rutes": [rute.uuid for rute, _ in db.session.query(Rute, competition.CompetitionRutes).filter(
             competition.CompetitionRutes.comp == comp.uuid).filter(competition.CompetitionRutes.rute == Rute.uuid)]
         }

    return jsonify(r), 200


@app.route('/get_comps', methods=['GET'])
def get_comps():
    r = [{"uuid": comp.uuid,
         "name": comp.name,
         "date": str(comp.date),
         "edit": str(comp.edit),
         "start": str(comp.start),
         "stop": str(comp.stop),
         "type": comp.type,
         "admins": comp.admins.split(","),
         "pin": comp.pin,
         "rutes": [rute.uuid for rute, _ in db.session.query(Rute, competition.CompetitionRutes).filter(
             competition.CompetitionRutes.comp == comp.uuid).filter(competition.CompetitionRutes.rute == Rute.uuid)]
         } for comp in db.session.query(competition.Competition)]

    return jsonify(r), 200


@app.route('/get_part', methods=['POST'])
def get_participation():
    comp = request.json['comp']
    user = request.json['user']

    part = db.session.query(competition.CompetitionParticipation).filter_by(comp=comp, user=user)
    if part is None:
        abort(400)

    r = [{"user": p.user,
          "comp": p.comp,
          "rute": p.rute,
          "tries": p.tries,
          "completed": p.completed,
          "date": str(p.date)} for p in part]

    return jsonify(r), 200


def parse_or_now(key, container):
    if key in container:
        return datetime.strptime(container[key],'%Y-%m-%d %H:%M:%S')
    else:
        return datetime.utcnow()


@app.route('/update_part', methods=['POST'])
def update_participation():
    comp = request.json['comp']
    user = request.json['user']
    rute = request.json['rute']
    tries = request.json['tries']
    date = parse_or_now("date", request.json)
    edit = parse_or_now("edit", request.json)
    completed = request.json['completed']

    part = db.session.query(competition.CompetitionParticipation).filter_by(comp=comp, user=user, rute=rute).first()
    if part is None:
        db.session.add(competition.CompetitionParticipation(comp=comp, user=user, rute=rute, tries=tries, completed=completed, date=date, edit=edit))
        db.session.commit()
    else:
        part.tries = tries
        part.completed = completed
        part.edit = edit
        db.session.commit()

    return "Success", 200


@app.route('/update_comp', methods=['POST'])
def update_comp():
    uuid = request.json['uuid']
    name = request.json['name']
    date = parse_or_now("date", request.json)
    edit = parse_or_now("edit", request.json)
    start = parse_or_now("start", request.json)
    stop = parse_or_now("stop", request.json)
    type = request.json['type']
    admins = request.json['admins']

    comp = db.session.query(competition.Competition).filter_by(uuid=uuid).first()
    if comp is None:
        pin = randint(1000,9999)
        while db.session.query(competition.Competition).filter_by(pin=pin).first():
            pin = randint(1000, 9999)
        db.session.add(competition.Competition(uuid=uuid, name=name, edit=edit, start=start, stop=stop, type=type, admins=admins, date=date, pin=pin))
        db.session.commit()
    else:
        comp.name = name
        comp.edit = edit
        comp.start = start
        comp.stop = stop
        comp.type = type
        comp.admins = admins
        db.session.commit()

    return "Success", 200


if __name__ == "__main__":

    import sys
    if "db" in sys.argv or not os.path.exists(get_sql_position()):
        print("Creates database")
        db.create_all()
        db.session.add(Gym(uuid="UnknowGym", name="Unknown Gym", lat=1, lon=1))
        db.session.add(User(uuid="admin", name="admin", password="admin", email="", gym="UnknowGym", role="ADMIN"))
        db.session.commit()


    app.run(debug=True)
