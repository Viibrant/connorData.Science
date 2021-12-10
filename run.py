from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from proj.covid import app as covid_app
from server import app as server

app = DispatcherMiddleware(server, {"/covid": covid_app})

if __name__ == "__main__":
    run_simple("localhost", 5000, app, use_reloader=False)
