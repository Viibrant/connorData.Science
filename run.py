from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound

from proj.covid import server as covid_app
from website import app as main

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(NotFound(), {"/app1": covid_app, "/app2": main})

if __name__ == "__main__":
    app.run()
