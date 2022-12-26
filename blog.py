import os

import requests
from flask import render_template, request, redirect, url_for
from flask_dance.contrib.discord import make_discord_blueprint, discord
from app import app
from model import *

discord_blueprint = make_discord_blueprint(redirect_to='blog')
app.register_blueprint(discord_blueprint, url_prefix="/login")


@app.route('/blog')
def blog():
    # get discord user info
    user = discord.get('/api/v10/users/@me')

    db.create_all()
    # grab needed databases
    entries = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()
    comments = BlogComments.query.order_by(BlogComments.date_created).all()

    return render_template("blog.html", entries=entries, comments=comments, discord=discord, user=user.json())

@app.route('/logout')
def logoutDiscord():
    # send user data to revoke uri
    resp = discord.post(
        "https://discord.com/api/oauth2/token/revoke",
        data={"client_id": os.environ['DISCORD_CLIENT_ID'], "client_secret": os.environ['DISCORD_CLIENT_SECRET'], "token": discord_blueprint.token["access_token"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    # also do this too!
    del discord_blueprint.token
    return redirect('/blog')

@app.route('/blog/<int:id>')
def blogOpenPost(id):
    # get discord user info
    user = discord.get('/api/v10/users/@me')

    db.create_all()
    # grab needed databases
    entries = BlogEntries.query.order_by(BlogEntries.date_created.desc()).all()
    comments = BlogComments.query.order_by(BlogComments.date_created).all()

    return render_template("blog.html", entries=entries, comments=comments, discord=discord, user=user.json(),
                           openId=id)


@app.route('/blog', methods=["POST"])
def blogPost():
    if request.method != 'POST':
        return


    if request.form.get('CommentSubmit') == 'Submit Comment':
        # grab information from needed inputs of form
        blog_id = int(request.form.get('BlogId'))
        comment = request.form.get('CommentWrite')
        userid = request.form.get('userid')
        user = request.form.get('username')
        avatar = request.form.get('avatar')
        date_created = datetime.now()

        # make new database object and commit it to db
        new_comment = BlogComments(blog_id=blog_id, user_id=userid, user=user, avatar_hash=avatar, comment=comment, date_created=date_created)
        db.session.add(new_comment)
        db.session.commit()


        return redirect(f"/blog/{blog_id}")



@app.route('/blog/<string:tag>', methods=["POST", "GET"])
def blogFilter(tag):
    # sort database by filter
    entries = BlogEntries.query.filter(BlogEntries.tag == tag).order_by(BlogEntries.date_created.desc()).all()

    return render_template("blog.html", entries=entries)
