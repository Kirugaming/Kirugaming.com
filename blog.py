import concurrent.futures
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
    return redirect("/blog/all/0")


# /blog/(blog type you want to filter by)/(blog post that is open when page loads (usually for loading post after
# commenting))
@app.route('/blog/<string:tag>/<int:blog_id>', methods=["POST", "GET"])
def blogFilter(tag, blog_id):
    # get discord user info
    user = discord.get('/api/v10/users/@me')
    # sort database by filter
    # use pagination to reduce load times
    page = request.args.get("page", 1, type=int)
    per_page = 10
    if tag == "all":
        entries = BlogEntries.query.order_by(BlogEntries.date_created.desc()).paginate(page, per_page, False)
    else:
        entries = BlogEntries.query.filter(BlogEntries.tag == tag).order_by(BlogEntries.date_created.desc()).paginate(
            page, per_page, False)

    comments = BlogComments.query.order_by(BlogComments.date_created).paginate(page, per_page, False)

    # check if pfp's are outdated
    checkAndUpdatePfps(comments)

    return render_template("blog.html", entries=entries, comments=comments, discord=discord, user=user.json(),
                           openId=blog_id)


def checkAndUpdatePfp(comment):
    # check comment for old pfp
    if requests.get(
            f"https://cdn.discordapp.com/avatars/{comment.user_id}/{comment.avatar_hash}.png").status_code == 404:
        # I HATE that i have to use a bot here because it will return unauthorized otherwise
        response = requests.get(f'https://discord.com/api/users/{comment.user_id}',
                                headers={'Authorization': f'Bot {os.environ["BLOG_BOT_TOKEN"]}'})
        if response.status_code == 200:  # the happy http code
            the_comment_in_question = BlogComments.query.filter_by(id=comment.id).first()
            the_comment_in_question.avatar_hash = response.json()['avatar']  # the update in question
            db.session.commit()
        else:
            print(f'Error: {response.status_code} - {response.text}')


def checkAndUpdatePfps(comments):
    # update comments pfps with multi-threading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # submit each comment to the thread pool
        futures = [executor.submit(checkAndUpdatePfp, comment) for comment in comments.items]
        # wait for all threads to complete
        concurrent.futures.wait(futures)


@app.route('/logout')
def logoutDiscord():
    # send user data to revoke uri
    resp = discord.post(
        "https://discord.com/api/oauth2/token/revoke",
        data={"client_id": os.environ['DISCORD_CLIENT_ID'], "client_secret": os.environ['DISCORD_CLIENT_SECRET'],
              "token": discord_blueprint.token["access_token"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    # also do this too!
    del discord_blueprint.token
    return redirect('/blog')


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
        new_comment = BlogComments(blog_id=blog_id, user_id=userid, user=user, avatar_hash=avatar, comment=comment,
                                   date_created=date_created)
        db.session.add(new_comment)
        db.session.commit()

        return redirect(f"/blog/all/{blog_id}")
