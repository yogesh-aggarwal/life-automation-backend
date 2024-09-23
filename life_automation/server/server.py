import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from flask_cors import CORS

from life_automation.core.constants import ALLOWED_ORIGINS
from .routes.auth.router import auth_router
from .routes.publishing.router import publishing_router

app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)

app.register_blueprint(auth_router, url_prefix="/auth")
app.register_blueprint(publishing_router, url_prefix="/publishing")


@app.get("/health")
def health():
    return "OK", 200


# Wrap the Flask app in ASGI
asgi_app = WsgiToAsgi(app)


def start_server():
    uvicorn.run(asgi_app, host="0.0.0.0", port=3000, log_level="info")
