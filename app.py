from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)


class BlogEntries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<entry %r>' % self.id


class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, nullable=False)
    password = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<account %r>' % self.id


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

    return redirect("/entrywriter")


@app.route('/entrywriter', methods=["POST", "GET"])
def entryWriter():
    if request.method != "POST":
        return render_template("entryWriter.html")

    entry_title = request.form['title']
    entry_content = request.form['blogContent']
    entry_tag = request.form['tag']
    new_entry = BlogEntries(title=entry_title, content=entry_content, tag=entry_tag)

    try:
        db.session.add(new_entry)
        db.session.commit()
        return redirect("/blog")
    except:
        return "There was an error adding this entry to the blog :("


if __name__ == '__main__':
    app.run(debug=True)
