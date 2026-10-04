from . import db
from datetime import datetime

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='user')
    active = db.Column(db.Boolean, default=True)
    blacklisted = db.Column(db.Boolean, default=False)
    time_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    #Relationships
    staff_profile = db.relationship('Staff', backref='user', lazy=True, uselist=False) 

    bookings = db.relationship('Booking', backref='user', lazy=True)
    
    assigned_treks = db.relationship('Trek', backref='assigned_staff', lazy=True, foreign_keys='Trek.assigned_staff_id')