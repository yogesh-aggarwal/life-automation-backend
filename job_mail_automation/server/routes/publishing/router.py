from flask import Blueprint

from job_mail_automation.server.middlewares.auth import \
    firebase_auth_middleware

from .medium.router import medium_router

publishing_router = Blueprint("publishing_router", __name__)

publishing_router.before_request(firebase_auth_middleware)

publishing_router.register_blueprint(medium_router, url_prefix="/medium")
