from flask import render_template

from app import app
from model import *


@app.route('/admin', methods=["POST", "GET"])
def admin():
    posts = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()
    projects = Projects.query.order_by(Projects.date_created.desc()).all()
    return render_template("adminDashboard.html", posts=posts, projects=projects)
