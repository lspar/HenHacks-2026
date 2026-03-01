

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


def get_emails(filter_type=None, keywords=None):
    import imaplib, email, os

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
    mail.select("inbox")

    if filter_type == "unread":
        status, data = mail.search(None, "UNSEEN")
    else:
        status, data = mail.search(None, "ALL")

    email_ids = data[0].split()
    messages = []

    for i in email_ids[-20:]:  # last 20 emails
        status, msg_data = mail.fetch(i, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg["subject"]
        sender = msg["from"]

        if keywords and subject:
            subject_lower = subject.lower()
            keyword_list = [k.strip().lower() for k in keywords.split(",")]
            if not any(k in subject_lower for k in keyword_list):
                continue  # skip emails that don't match

        messages.append({"subject": subject, "from": sender})

    mail.logout()
    return messages

@app.route("/check-emails")
def check_emails():
    keywords = "internship"  # you can make this dynamic later
    filter_type = "unread"   # or "all"

    emails = get_emails(filter_type=filter_type, keywords=keywords)
    return render_template("emails.html", emails=emails)

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





