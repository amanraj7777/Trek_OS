from . import db

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    contact_number = db.Column(db.String(10), nullable=False)
    experience = db.Column(db.Text, nullable=False)
    approved_status = db.Column(db.String(20), nullable=False, default='pending')