from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/index")
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

app.run(debug=True)