from flask import Flask, render_template, request
from os import getcwd
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

@app.route("/update_server", mehods=["POST"])
def webhook():
    if request.method == "POST":
        repo = git.Repo(getcwd())
        origin = repo.remotes.origin
        origin.pull()
        return "Updated PythonAnywhere successfully", 200
    return "Wrong event type", 400

if __name__ == "__main__":
    app.run(debug=True)