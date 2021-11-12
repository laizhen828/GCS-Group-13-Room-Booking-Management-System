from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db

class Bookings(db.Model):
    __tablename__ = 'bookings'
    num_log = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.String(10))
    time_slot = db.Column(db.String(13))
    approve_status = db.Column(db.String(8))
    booked_by = db.Column(db.String(20), db.ForeignKey('credentials.username'))
    approved_declined_by = db.Column(db.String(20))
    room_type =  db.Column(db.String(100))

class Credentials(db.Model, UserMixin):
    __tablename__ = 'credentials'
    def get_id(self):
        return (self.username)
    username = db.Column(db.String(20), primary_key=True, unique=True)
    name = db.Column(db.String(30))
    email = db.Column(db.String(30))
    priv = db.Column(db.String(10))
    password = db.Column(db.String(1000))

class Notifications(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.String(20), primary_key=True)
    model = db.Column(db.String(30))
    location = db.Column(db.String(30))

class Rooms(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_type = db.Column(db.String(100))
    abbr = db.Column(db.String(10))
    quantity = db.Column(db.Integer)

