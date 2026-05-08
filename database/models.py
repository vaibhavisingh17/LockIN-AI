from database.db import db

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(100))


class StudySession(db.Model):

    __tablename__ = 'study_sessions'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    study_hours = db.Column(db.Float)

    sleep_hours = db.Column(db.Float)

    mood = db.Column(db.Integer)

    distractions = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)