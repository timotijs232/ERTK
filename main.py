from flask import Flask,render_template,request,redirect,url_for,session
import requests
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'hujzin'


@app.route("/")

@app.route("/")
def testam():
    return render_template('testam.html')

@app.route("/sakums")
def sakums():
    return render_template('sakums.html')

@app.route("/novietojums")
def novietojums():
    return render_template('novietojums.html')

@app.route("/gribikreslu")
def gribikreslu():
    return render_template('gribikreslu.html')

@app.route("/autorizeties", methods=["GET", "POST"])
def autorizeties():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Lietotājs jau eksistē!"
        finally:
            conn.close()

        return redirect(url_for("sakums"))
    
    return render_template('autorizeties.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("sakums"))
        else:
            return "Nepareizs e-pasts vai parole."

    return render_template("login.html")

@app.route("/atsauksme", methods=["GET", "POST"])
def atsauksme():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":

        print("Formas dati:")
        print(request.form)

        atsauksme_text = request.form["atsauksme"]
        user_id = session["user_id"]

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO reviews (user_id, review) VALUES (?, ?)", (user_id, atsauksme_text))
        conn.commit()
        conn.close()

        return redirect(url_for("atsauksmes"))
    
    return render_template("atsauksme.html")


@app.route("/atsauksmes")
def atsauksmes():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
        SELECT users.username, reviews.review, reviews.created_at
        FROM reviews
        JOIN users ON reviews.user_id = users.id
        ORDER BY reviews.created_at DESC
    """)
    all_reviews = c.fetchall()
    conn.close()

    return render_template("atsauksmes.html", atsauksme=all_reviews)

@app.route("/iztirit", methods=["POST"])
def iztirit():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("username") != "tomsboss":
        return redirect(url_for("atsauksmes"))
        
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM reviews")
    conn.commit()
    conn.close()

    return redirect(url_for("atsauksmes"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("sakums"))

app.run(debug=True,host='0.0.0.0',port=80)