from server import app
from flask import request, abort, jsonify
from db import db
from datetime import datetime

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String)
    name = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    edit = db.Column(db.DateTime, default=datetime.utcnow)
    start = db.Column(db.DateTime, default=datetime.utcnow)
    stop = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.Integer)
    admins = db.Column(db.String)
    pin = db.Column(db.Integer)


class CompetitionParticipation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)
    comp = db.Column(db.String)
    rute = db.Column(db.String)
    tries = db.Column(db.Integer)
    completed = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    edit = db.Column(db.DateTime, default=datetime.utcnow)


class CompetitionRutes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comp = db.Column(db.String)
    rute = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)




