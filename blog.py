from flask import render_template

from app import app
from model import *


@app.route('/blog', methods=["POST", "GET"])
def blog():
    db.create_all()
    entries = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()

    return render_template("blog.html", entries=entries)


@app.route('/blog/<tag>', methods=["POST", "GET"])
def blogFilter(tag):
    entries = BlogEntries.query.filter(BlogEntries.tag == tag).order_by(BlogEntries.date_created.desc()).all()

    return render_template("blog.html", entries=entries)
