import flask_login
import requests
import json
from flask import Flask, render_template, request, redirect, url_for
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'amongus'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
ckeditor = CKEditor(app)


# Create a table for blog entries
class BlogEntries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<entry %r>' % self.id


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


@login_manager.user_loader
def load_user(user_id):
    user = Accounts.query.filter_by(id=user_id).first()
    if user:
        return user
    return None


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("aboutme.html")


@app.route('/blog', methods=["POST", "GET"])
def blog():
    db.create_all()
    entries = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()

    return render_template("blog.html", entries=entries)


@app.route('/blog/<tag>', methods=["POST", "GET"])
def blogFilter(tag):
    entries = BlogEntries.query.filter(BlogEntries.tag == tag).order_by(BlogEntries.date_created.desc()).all()

    return render_template("blog.html", entries=entries)


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method != "POST":
        return render_template("login.html")

    check_username = request.form["username"]
    check_password = request.form["password"]
    if Accounts.query.filter_by(username=check_username) is None or not check_password_hash(
            Accounts.query.filter_by(username=check_username).first().password, check_password):
        return "Wrong username or password"

    user = Accounts.query.filter_by(username=check_username).first()
    login_user(user)

    return redirect("/entrywriter")


@app.route('/entrywriter', methods=["POST", "GET"])
@flask_login.login_required
def entryWriter():
    entries = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()

    if request.method != "POST":
        return render_template("entryWriter.html", entries=entries)

    entry_title = request.form['title']
    entry_content = request.form['ckeditor']
    entry_tag = request.form['tag']
    new_entry = BlogEntries(title=entry_title, content=entry_content, tag=entry_tag)

    try:
        # Push webhook to discord server
        webhook_content = {
            "content": None,
            "embeds": [
                {
                    "title": f"{entry_title}",
                    "description": "Go check it out!",
                    "url": "https://Kirugaming.com/blog",
                    "color": 6225920,
                    "author": {
                        "name": "A new post was added to the blog!"
                    },
                    "timestamp": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "image": {
                        "url": "https://c.tenor.com/OKVIq4Vx3r0AAAAd/dangerous-bear.gif"
                    }
                }
            ],
            "attachments": []
        }
        requests.post(
            'https://discord.com/api/webhooks/1003124317992779846/VUrG8AhZ2rONLsKX4XeoM6oMrZXCC9TzkWmdE3ORvQeL4KGPBfq8lP66bOuOBH4KSaU4',
            data=json.dumps(webhook_content),
            headers={'Content-Type': 'application/json'})
        # Add entry to database
        db.session.add(new_entry)
        db.session.commit()
        return redirect("/blog")
    except:
        return "There was an error adding this entry to the blog :("


@app.route('/entrywriter/update/<int:id>', methods=["POST", "GET"])
@flask_login.login_required
def editEntry(id):
    entries = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()

    if request.method != "POST":
        entry = BlogEntries.query.filter_by(id=id).first()
        return render_template("editEntry.html", entry=entry)

    entry_title = request.form['title']
    entry_content = request.form['ckeditor']
    entry_tag = request.form['tag']
    entry = BlogEntries.query.filter_by(id=id).first()
    entry.title = entry_title
    entry.content = entry_content
    entry.tag = entry_tag

    try:
        db.session.commit()
        return redirect("/blog")
    except:
        return "There was an error adding this entry to the blog :("


@app.route('/entrywriter/delete/<int:id>', methods=["POST", "GET"])
@flask_login.login_required
def deleteEntry(id):
    entry = BlogEntries.query.filter_by(id=id).first()
    try:
        db.session.delete(entry)
        db.session.commit()
        return redirect("/blog")
    except:
        return "There was an error deleting this entry from the blog :("


if __name__ == '__main__':
    app.run(host="0.0.0.0")
