import os
from dotenv import load_dotenv
from helpers import apology, login_required

from flask import Flask, session
from flask.templating import render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import time
import json
import requests

app = Flask(__name__)
load_dotenv("./env")
FLASK_APP = os.getenv("FLASK_APP")
DATABASE_URL = os.getenv("DATABASE_URL")

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return render_template("home.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/Ejemplo")
def Ejemplo():
    all = db.execute(""" SELECT * FROM "Comment" """).fetchall()

    print(all)

    return ""

@app.route("/BookPage", methods=["POST", "GET"])
@login_required
def bookpage():
    ISBN = request.args.get("ISBN")

    book = db.execute("""SELECT * FROM "Book" WHERE "ISBN" = :isbn""", {"isbn" : ISBN}).fetchone()

    if request.method == "POST":
    
        # # # # # # # # # # # # # # # ENVIO DE RESEÑAS # # # # # # # # # # # # # # # # # # #

        # hash the password and insert a new user in the database
        db.execute("""INSERT INTO "Comment" ("Comment", "Id_User", "Id_Book", "Date_Time", "Rate") VALUES (:comment, :iduser, :idbook, :date_time, :rate) """, {"comment": request.form.get("CText"), "iduser": session["user_id"], "idbook": book["Id_Book"], "date_time" : time.strftime("%c"), "rate" : request.form.get("CRate")})

        # Remember which user has logged in
        db.commit()

    band = db.execute(""" SELECT * FROM "Comment" WHERE "Id_User" = :iduser AND "Id_Book" = :idbook """, {"iduser" : session["user_id"], "idbook" : book["Id_Book"]}).fetchall()

    comments = db.execute(""" SELECT * FROM "Comment" INNER JOIN "User" ON "User"."Id_User" = "Comment"."Id_User" WHERE "Id_Book" = :idbook """, {"idbook" : book["Id_Book"]}).fetchall()

    # # # # # # # # # # # # # # INFORMACION DESDE LA API DE GOOGLE BOOKS # # # # # # # # # # # # # # # # #

    response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + ISBN).json()

    librito = []
    if response["totalItems"] != 0:     
        librito.append(response["items"][0]["volumeInfo"]["description"])
        librito.append(response["items"][0]["volumeInfo"]["averageRating"])
        librito.append(response["items"][0]["volumeInfo"]["ratingsCount"])
        librito.append(response["items"][0]["volumeInfo"]["imageLinks"]["smallThumbnail"])
    else:
        librito.append("Not Found on API")
        librito.append("Not Found on API")
        librito.append("Not Found on API")
        librito.append(
            "https://planetadelibrospe5.cdnstatics.com/usuaris/libros/fotos/271/m_prensa/270751_gravity-falls-diario-3_9789584265159_3d.png")

    band = len(band)

    return render_template("/bookpage.html", book = book, Band = band, comments = comments, librito = librito)

################################# API #######################################

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):

    ISBN = isbn

    book = db.execute("""SELECT * FROM "Book" WHERE "ISBN" = :isbn""", {"isbn": ISBN}).fetchone()

    if book:
        comments = db.execute(""" SELECT AVG("Rate"), COUNT("Rate") FROM "Comment" WHERE "Id_Book" = :idbook """, {"idbook" : book["Id_Book"]}).fetchone()

        respuesta = {
            "title": book["Title"],
            "author": book["Author"],
            "year": book["YearB"],
            "isbn": book["ISBN"],
            "review_count": str(comments[1]),
            "average_score": str(comments[0])
        }

        return json.dumps(respuesta)
    else:
        return "Sorry" # CREAR UN JSON EN LUGAR DE ESTE STRING

####################################################################

@app.route("/list", methods=["POST", "GET"])
@login_required
def list():
    
    if request.method == 'GET':
        books = db.execute("""SELECT * FROM "Book" ORDER BY "Title" ASC""").fetchall()

        return render_template("list.html", books = books[0 : 30])
    else:
        q = request.form.get('q')

        if not q:
            books = db.execute("""SELECT * FROM "Book" ORDER BY "Title" ASC""").fetchall()

            return render_template("books.html", books = books[0 : 30])
        
        q = '%' + q.capitalize() + '%'

        books = db.execute("""SELECT * FROM "Book" WHERE "ISBN" LIKE :q OR "Title" LIKE :q OR "Author" LIKE :q""", {"q" : q}).fetchall()

        return render_template("books.html", books = books[0 : 30])


@app.route("/register", methods=["POST", "GET"])
def register():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # hash the password and insert a new user in the database
        password = generate_password_hash(request.form.get("TxtPasswordR"))
        result = db.execute("""INSERT INTO "User" ("Username", "Email", "Pass") VALUES (:Username, :Email, :Pass) returning "Id_User" """, {
            "Username": request.form.get("TxtUserR"), "Email": request.form.get("TxtEmailR"), "Pass": password}).fetchone()[0]

        # Remember which user has logged in
        session["user_id"] = result
        db.commit()

        # Display a flash message
        flash("Registered!")

        # Redirect user to home page
        return redirect("/register")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        """
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        """

        # Query database for username
        rows = db.execute("""SELECT * FROM "User" WHERE "Username" = :Username""",
                          {"Username": request.form.get("TxtuserL")}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][3], request.form.get("TxtpassL")):
            return redirect("/register")
        else:
            # Remember which user has logged in
            session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/list")
