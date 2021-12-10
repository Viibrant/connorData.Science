from werkzeug.middleware.dispatcher import DispatcherMiddleware
from proj.covid import server as covid_dashboard
from website import app as website

webapp = DispatcherMiddleware(
    website.wsgi_app, {"/covid_dashboard": covid_dashboard.wsgi_app}
)
