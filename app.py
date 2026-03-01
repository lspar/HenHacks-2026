

from flask import Flask, render_template, session, redirect, url_for, request
from google_auth_oauthlib.flow import InstalledAppFlow
from werkzeug.security import generate_password_hash, check_password_hash
import os
import firebase_admin
from firebase_admin import credentials, firestore

db = None

if os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    print("Warning: serviceAccountKey.json not found. Firestore features will be disabled.")

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret"

@app.route("/")
def home_page():
    user_email = session.get("google_email")
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
    return render_template("dashboard.html")

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


# Google login
@app.route("/login")
def login():
   flow = InstalledAppFlow.from_client_secrets_file(
       'credentials.json',
       scopes=['https://www.googleapis.com/auth/userinfo.email']
   )
   credentials = flow.run_local_server(port=5002)
   # save their email in the session
   session['google_email'] = credentials.id_token['email']
   return redirect(url_for("dashboard"))

if __name__ == "__main__":
   app.run(port=5002, debug=True)


