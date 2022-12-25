import os
from dotenv import load_dotenv

from flask import Flask
from flask_ckeditor import CKEditor

from model import *

app = Flask(__name__)
load_dotenv(override=True)
app.secret_key = os.environ['SECRET_KEY']
app.config["DISCORD_OAUTH_CLIENT_ID"] = os.environ['DISCORD_CLIENT_ID']
app.config["DISCORD_OAUTH_CLIENT_SECRET"] = os.environ['DISCORD_CLIENT_SECRET']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # set 1 for testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db.init_app(app)
from blog import *
from admin import *

login_manager.init_app(app)
ckeditor = CKEditor(app)

db.create_all(app=app)


@app.route('/', methods=["GET"])
def home():
    projects = Projects.query.order_by(Projects.date_created.desc()).all()
    return render_template("index.html", projects=projects)


@app.route('/about')
def about():
    return render_template("aboutme.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
