from flask import Flask
from flask_ckeditor import CKEditor

from model import *

app = Flask(__name__)
app.secret_key = 'amongus'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db.init_app(app)
from blog import *
from admin import *

login_manager.init_app(app)
ckeditor = CKEditor(app)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("aboutme.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
