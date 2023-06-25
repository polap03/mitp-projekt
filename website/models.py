from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, date

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    organizer_emails = ['maja.shaja@gmail.com', 'ola.lola@gmail.com']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    notes = db.relationship('Ad')
    role = db.Column(db.String(50), nullable=False)

class Participant(db.Model):
    __tablename__ = 'participants'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    shirt_size = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)

    def __init__(self, first_name, last_name, email, shirt_size, gender, phone_number, birthdate):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.shirt_size = shirt_size
        self.gender = gender
        self.phone_number = phone_number
        self.birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()

        