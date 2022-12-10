import requests, markdown
from flask import render_template, request, redirect

from app import app
from model import *


def convertMarkdownToHTML(projectMarkdown):
    html = markdown.markdown(projectMarkdown)
    title = html.splitlines()[0].replace("<h1>", "").replace("</h1>", "")
    return title, html



@app.route('/admin', methods=["POST", "GET"])
def admin():
    if request.method != "POST":
        posts = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()
        projects = Projects.query.order_by(Projects.date_created.desc()).all()

        return render_template("adminDashboard.html", posts=posts, projects=projects)

    if request.form['SubmitProject'] == 'SubmitProject':
        project_link = request.form['ProjectLink']

        readme = project_link.replace('github.com', 'raw.githubusercontent.com').replace('https://', 'https://').replace('http://', 'https://').replace('github.com', 'raw.githubusercontent.com').replace('blob/', '')
        readme += '/master/README.md'
        convertMarkdownToHTML(requests.get(readme).text)

        project_title = convertMarkdownToHTML(requests.get(readme).text)[0]
        project_description = convertMarkdownToHTML(requests.get(readme).text)[1]

        date_created = datetime.now()
        new_project = Projects(title=project_title, description=project_description, link=project_link, date_created=date_created)
        db.session.add(new_project)
        db.session.commit()
        return redirect("/")
