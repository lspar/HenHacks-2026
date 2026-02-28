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

