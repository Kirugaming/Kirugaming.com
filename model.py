from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

# create database without circular import
db = SQLAlchemy()


# Create a table for blog entries
class BlogEntries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<entry %r>' % self.id


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<project %r>' % self.id


# Create a table for accounts
class Accounts(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, nullable=False)
    password = db.Column(db.Integer, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<account %r>' % self.id
