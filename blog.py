import requests
from flask import render_template, request, redirect, url_for
from flask_dance.contrib.discord import make_discord_blueprint, discord
from app import app
from model import *

discord_blueprint = make_discord_blueprint(redirect_to='blog')
app.register_blueprint(discord_blueprint, url_prefix="/login")


@app.route('/blog')
def blog():
    user = discord.get('/api/v10/users/@me')

    db.create_all()
    entries = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()
    comments = BlogComments.query.order_by(BlogComments.date_created.desc()).all()

    return render_template("blog.html", entries=entries, comments=comments, discord=discord, user=user.json())


@app.route('/blog', methods=["GET"])
def blogGet():


    print("test")
    # form will bring to here were it will log in through discord OAuth2 so blog can get user information
    if not discord.authorized:
        if request.method == 'GET':
            return redirect(url_for("discord.login"))

        user = discord.get('/api/v10/users/@me')
        assert user.ok, user.text
        print(user.status_code)
        print(user.text)


@app.route('/blog', methods=["POST"])
def blogPost():
    print("test")
    if request.method != 'POST':
        return

    # TEST

    if request.form.get('CommentSubmit') == 'Submit Comment':
        blog_id = int(request.form.get('BlogId'))
        comment = request.form.get('CommentWrite')
        userid = request.form.get('userid')
        user = request.form.get('username')
        avatar = request.form.get('avatar')
        date_created = datetime.now()

        new_comment = BlogComments(blog_id=blog_id, user_id=userid, user=user, avatar_hash=avatar, comment=comment, date_created=date_created)
        db.session.add(new_comment)
        db.session.commit()

        return redirect("/blog")


@app.route('/blog/<tag>', methods=["POST", "GET"])
def blogFilter(tag):
    entries = BlogEntries.query.filter(BlogEntries.tag == tag).order_by(BlogEntries.date_created.desc()).all()

    return render_template("blog.html", entries=entries)
