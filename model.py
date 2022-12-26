from datetime import datetime, timezone
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

    def serialize(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'title': self.title,
            'content': self.content,
            'date_created': self.date_created
        }

    def __repr__(self):
        return '<entry %r>' % self.id


class BlogComments(db.Model):
    blog_id = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(200), nullable=False)
    avatar_hash = db.Column(db.String(200), nullable=False)
    comment = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def serialize(self):
        return {
            'blog_id': self.blog_id,
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user,
            'avatar_hash': self.avatar_hash,
            'comment': self.comment,
            'date_created': self.date_created
        }

    def __repr__(self):
        return '<comment %r>' % self.id


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<project %r>' % self.id


class Accounts(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, nullable=False)
    password = db.Column(db.Integer, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<account %r>' % self.id
