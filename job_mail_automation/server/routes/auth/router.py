from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field

from job_mail_automation.core.firebase import auth
from job_mail_automation.types.user import User

from .google.router import google_auth_router

auth_router = Blueprint("auth_router", __name__)

auth_router.register_blueprint(google_auth_router, url_prefix="/google")


class SignupRequestBody(BaseModel):
    uid: str = Field(..., alias="uid")
    name: str = Field(..., alias="name")
    email: str = Field(..., alias="email")
    dp: str = Field(..., alias="dp")


@auth_router.post("/signup")
def signup():
    # Step 1: Validate body
    try:
        body = SignupRequestBody.model_validate(request.json)
    except:
        return jsonify({"message": "invalid_body_content"}), 403

    # Step 2: Create user
    try:
        User.create(id=body.uid, email=body.email, name=body.name, dp=body.dp)
    except:
        return jsonify({"message": "internal_server_error"}), 500

    return jsonify({"message": "success"}), 200