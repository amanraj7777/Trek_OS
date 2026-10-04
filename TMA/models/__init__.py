from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Import models to register them with SQLAlchemy
from .users import Users
from .staff import Staff
from .trek import Trek
from .booking import Booking
