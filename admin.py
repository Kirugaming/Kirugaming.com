import json

import flask_login
import requests, markdown
from flask import render_template, request, redirect
from flask_login import login_user, LoginManager
from werkzeug.security import check_password_hash

from app import app
from model import *

login_manager = LoginManager()
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return user if (user := Accounts.query.filter_by(id=user_id).first()) else None


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

    return redirect("/admin")


def convertMarkdownToHTML(projectMarkdown):
    html = markdown.markdown(projectMarkdown)
    title = html.splitlines()[0].replace("<h1>", "").replace("</h1>", "")
    return title, html


@app.route('/admin', methods=["POST", "GET"])
@flask_login.login_required
def admin():
    if request.method != "POST":
        posts = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()
        # seralize each in list
        posts = [post.serialize() for post in posts]

        comments = BlogComments.query.order_by(BlogComments.date_created.desc()).all()
        comments = [comment.serialize() for comment in comments]

        projects = Projects.query.order_by(Projects.date_created.desc()).all()

        return render_template("adminDashboard.html", posts=posts, projects=projects, comments=comments)

    if request.form.get('SubmitProject') == 'SubmitProject':
        project_link = request.form['ProjectLink']

        readme = project_link.replace('github.com', 'raw.githubusercontent.com').replace('https://',
                                                                                         'https://').replace('http://',
                                                                                                             'https://').replace(
            'github.com', 'raw.githubusercontent.com').replace('blob/', '')
        readme += '/master/README.md'

        project_title = convertMarkdownToHTML(requests.get(readme).text)[0]
        project_description = convertMarkdownToHTML(requests.get(readme).text)[1]

        date_created = datetime.now()
        new_project = Projects(title=project_title, description=project_description, link=project_link,
                               date_created=date_created)
        db.session.add(new_project)
        db.session.commit()
        return redirect("/")

    if request.form.get('SubmitPost') == 'SubmitPost':
        entry_title = request.form.get('blogTitle')
        entry_content = request.form.get('ckeditor')
        entry_tag = request.form.get('tag')
        new_entry = BlogEntries(title=entry_title, content=entry_content, tag=entry_tag)

        # discord webhook
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
        except:
            return "failed to publish post"
    print(request.form)
    if request.form.get('UpdatePost') == 'UpdatePost':
        blog_id = request.form.get('BlogId')
        entry = BlogEntries.query.filter_by(id=blog_id).first()
        entry.title = request.form.get('updateBlogTitle')
        entry.content = request.form.get('ckeditor')
        entry.tag = request.form.get('tag')
        db.session.commit()
        return redirect("/blog")


@app.route('/admin/updateProject/<int:id>', methods=["POST", "GET"])
@flask_login.login_required
def updateProject(id):
    project = Projects.query.filter_by(id=id).first()
    project_link = project.link

    readme = project_link.replace('github.com', 'raw.githubusercontent.com').replace('https://',
                                                                                     'https://').replace('http://',
                                                                                                         'https://').replace(
        'github.com', 'raw.githubusercontent.com').replace('blob/', '')
    readme += '/master/README.md'

    project_description = convertMarkdownToHTML(requests.get(readme).text)[1]
    print(readme)
    try:
        project.description = project_description
        db.session.commit()
        return redirect("/")
    except:
        return "There was an error updating this project from the projects :("


@app.route('/admin/deleteProject/<int:id>', methods=["POST", "GET"])
@flask_login.login_required
def deleteProject(id):
    project = Projects.query.filter_by(id=id).first()
    try:
        db.session.delete(project)
        db.session.commit()
        return redirect("/admin")
    except:
        return "There was an error deleting this project from the projects :("


@app.route('/admin/deletePost/<int:id>', methods=["POST", "GET"])
@flask_login.login_required
def deletePost(id):
    post = BlogEntries.query.filter_by(id=id).first()
    try:
        db.session.delete(post)
        db.session.commit()
        return redirect("/admin")
    except:
        return "There was an error deleting this blog post from the entries :("

@app.route('/admin/deleteComment/<int:id>', methods=["POST", "GET"])
@flask_login.login_required
def deleteComment(id):
    comment = BlogComments.query.filter_by(id=id).first()
    db.session.delete(comment)
    db.session.commit()
    return redirect("/blog")
