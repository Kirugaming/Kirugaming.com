import flask_login
import json

import requests
from flask import request, render_template, redirect
from flask_login import login_user, LoginManager
from werkzeug.security import check_password_hash

from app import app
from model import *

login_manager = LoginManager()
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return user if (user := Accounts.query.filter_by(id=user_id).first()) else None


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
        webhook_content = {"content": None, "embeds": [
            {"title": f"{entry_title}", "description": "Go check it out!", "url": "https://Kirugaming.com/blog",
             "color": 6225920, "author": {"name": "A new post was added to the blog!"},
             "timestamp": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "image": {
                "url": "https://media.discordapp.net/attachments/821916065210433596/962010623204528249/5D827026-C8C3-41BE-AF6A-A0CAC4591BA0.gif"}}],
                           "attachments": []}

        requests.post(
            'https://discord.com/api/webhooks/1003124317992779846/VUrG8AhZ2rONLsKX4XeoM6oMrZXCC9TzkWmdE3ORvQeL4KGPBfq8lP66bOuOBH4KSaU4',
            data=json.dumps(webhook_content), headers={'Content-Type': 'application/json'})

        db.session.add(new_entry)
        db.session.commit()
        return redirect("/blog")
    except Exception:
        return "There was an error adding this entry to the blog :("


@app.route('/entrywriter/update/<int:id>', methods=["POST", "GET"])
@flask_login.login_required
def editEntry(id):
    entries = BlogEntries.query.order_by(BlogEntries.date_created).all()

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
