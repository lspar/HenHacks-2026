from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home_page():
    profile = ""
    if request.method == "POST":
        email = request.form["email"]
        keywords = request.form.getlist("keywords")
        # Simulate processing the email
        profile = f"Saved email: {email}, Keywords: {keywords}"
        return render_template("home.html", result=profile)
    return render_template("home.html")

from flask import Flask, render_template, session, redirect, url_for
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret"

@app.route("/")
def home_page():
    user_email = session.get("google_email")
    return render_template("home.html", user_email=user_email)
    

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# Google login
@app.route("/login")
def login():
   flow = InstalledAppFlow.from_client_secrets_file(
       'credentials.json',
       scopes=['https://www.googleapis.com/auth/userinfo.email']
   )
   credentials = flow.run_local_server(port=0)
   # save their email in the session
   session['google_email'] = credentials.id_token['email']
   return redirect(url_for("home_page"))


if __name__ == "__main__":
   app.run(port=5000, debug=True)

