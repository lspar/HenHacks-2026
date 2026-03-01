

from flask import Flask, render_template, session, redirect, url_for, request
from dotenv import load_dotenv
import imaplib, email, os
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret"

db = None

if os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    print("Warning: serviceAccountKey.json not found. Firestore features will be disabled.")

@app.route("/filter_emails", methods=["POST"])
def filter_emails():
    email = request.form.get("email_content")
    username = session.get("username")
    keywords = ["internship","opportunity", "job", "application"]

    for keyword in keywords:
        if keyword in email:
            db.collection("users").document(username).collection("email").add({
                "email": email
        })
    return redirect("/dashboard")



"""@app.route("/check-emails")
def check_emails():
    keywords = "internship"  # you can make this dynamic later
    filter_type = "unread"   # or "all"

    emails = get_emails(filter_type=filter_type, keywords=keywords)
    return render_template("emails.html", emails=emails)"""

@app.route("/")
def home_page():
    user_email = session.get("username")
    return render_template("home.html", user_email=user_email)

@app.route("/create-account", methods=["POST"])
def create_account():

    if db is None:
        return "Database not Connected"
    
    username = request.form.get("username")
    password = request.form.get("password")

    hashed_password = generate_password_hash(password)

    db.collection("users").document(username).set({
        "username": username,
        "password": hashed_password
    })

    return redirect(url_for("home_page"))
    

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/")

    username = session["username"]

    information = ""

    try:
        email_docs = db.collection("users").document(username).collection("email").stream()

        for doc in email_docs:
            data = doc.to_dict()
            information += data.get("email", "") + "\n\n"

    except Exception as e:
        print("Error fetching emails:", e)

    return render_template("dashboard.html", username=username, information=information)

@app.route("/new-app")
def new_app():
    return render_template("new.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/set-up")
def set_up():
    return render_template("set-up.html")

@app.route("/check-login", methods=["POST"])
def check_login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = db.collection("users").where("username", "==", username).get()
    if len(user) != 0:
        
        user_data = user[0].to_dict()
        if check_password_hash(user_data["password"], password):
            session["username"] = username
            return redirect("/dashboard")
        else:
            error = "Wrong Password"
            return redirect("/")
    else:
        error = "Create an account first"
        return redirect("/")
    

@app.route("/email")
def email():
    return render_template("email.html")





