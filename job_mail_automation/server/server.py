from flask import Flask

from .routes.auth.google.router import google_auth_router

app = Flask(__name__)

app.register_blueprint(google_auth_router, url_prefix="/auth/google")


def start_server():
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)
