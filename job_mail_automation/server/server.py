from flask import Flask
from flask_cors import CORS

from .routes.auth.google.router import google_auth_router

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(google_auth_router, url_prefix="/auth/google")


@app.get("/health")
def health():
    return "OK", 200


def start_server():
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)
