from . import db

class Trek(db.Model):
    __tablename__ = 'trek'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    max_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    description = db.Column(db.Text, default=' ')

    #Relationships
    bookings = db.relationship('Booking', backref='trek', lazy=True)