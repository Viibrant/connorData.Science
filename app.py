from flask import Flask, render_template, request
import os
import git
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cv")
def cv():
    return render_template("cv.html")

@app.route("/projects-grid-cards")
def projects():
    return render_template("projects-grid-cards.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/update_server", methods=["POST"])
def webhook():
    if request.method == "POST":
        x_hub_signature = request.headers.get("X-Hub-Signature")
        print(x_hub_signature)
        repo = git.Repo("/home/Viibrant/connorData.Science")
        origin = repo.remotes.origin
        origin.pull()
        return "Updated PythonAnywhere successfully", 200
    return "Wrong event type", 400

if __name__ == "__main__":
    app.run(debug=True)