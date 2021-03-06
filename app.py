﻿from flask import Flask, render_template, request, redirect, url_for, flash
import os
from flask import g
import sqlite3
import string

app = Flask(__name__, static_folder="static", static_path="")

# Secret key is needed to keep the client-side sessions secure
# os.urandom(n) returns a string of n random bytes
app.secret_key = os.urandom(24)

DB_FILE = "guestbook"

comments = []

usernameOutput = "user"



def insert_comment(comment):
    cursor = g.db.cursor()
    comment = cursor.execute("INSERT INTO comment(username, comment, DATE) values(?,?, date('now'))", (usernameOutput, comment))
    g.db.commit()
    return comment.lastrowid


def fetch_all_comment():
    cursor = g.db.cursor()
    cursor.execute("SELECT cm.username, cm.comment, f.image, u.name, u.city, cm.date FROM comment AS cm" +
                   " LEFT JOIN file AS f ON cm.commentid=f.commentid" +
                   " INNER JOIN USER U ON cm.username=U.username " +
                   " ORDER BY cm.date desc")

    listt = list(cursor.fetchall())
    return listt


@app.before_request
def before_request():
    g.db = sqlite3.connect('guestbook.db')


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def index():
    title = "STOCKHOLM"
    return render_template('index.html', title=title)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/guestbook')
def guestbook():
    return render_template("guestbook.html")


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        username = request.form["usernm"]
        password = request.form["passwd"]
        cursor = g.db.cursor()

        try:
            usernameDB = cursor.execute("SELECT USERNAME FROM USER WHERE USERNAME=?", [username]).fetchone()[0]
            passwordDB = cursor.execute("SELECT PASSWORD FROM USER WHERE USERNAME=?", [username]).fetchone()[0]

            if usernameDB == False:
                flash("No user with that name")
                return redirect(url_for("login"))
            elif password != passwordDB:
                flash("Incorrect username or password")
                return redirect(url_for("login"))
            else:
                flash("Logged in sucessfully")
                global usernameOutput
                usernameOutput = usernameDB
                return redirect(url_for("guestbookloggedin"))
        except (sqlite3.IntegrityError, TypeError):
            flash("Incorrect username or password")
            return render_template("login.html")

    return render_template("login.html")



@app.route('/guestbookloggedin', methods=['GET', 'POST'])
def guestbookloggedin():
    if request.method == "GET":

        return render_template('guestbookloggedin.html', comments=fetch_all_comment(), user=usernameOutput.upper())

    comment = request.form["commentContent"]
    commentid = insert_comment(comment)
    cursor = g.db.cursor()
    try:
        file = request.files['file']
        file.save(os.path.join("G:\www\hometown-webpage\static\images\\files", file.filename))
        filename = file.filename
        cursor.execute("INSERT INTO FILE (commentID, image) VALUES(?,?)", (commentid, filename))
        g.db.commit()
    except FileNotFoundError:
        pass

    return redirect(url_for('guestbookloggedin'))




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    try:
        name = request.form["name"]
        username = request.form["username"]
        city = request.form["city"]
        password = request.form["pwd"]
        cursor = g.db.cursor()

        cursor.execute("INSERT INTO USER (name, username, city, password) VALUES(?, ?, ?, ?)",
                       (name, username, city, password))
        g.db.commit()
        flash("Successfully registered")
        return redirect(url_for("guestbook"))
    except sqlite3.IntegrityError:
        flash("Something went wrong!")
        return redirect(url_for("register"))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
