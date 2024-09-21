import os

from flask import Blueprint, jsonify, request
from google.auth.transport import requests as google_requests
from google.cloud.firestore_v1.base_query import FieldFilter
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from job_mail_automation.core.constants import (
    GOOGLE_OAUTH_CLIENT_ID,
    GOOGLE_OAUTH_CLIENT_SECRET,
    REDIRECT_URI,
)
from job_mail_automation.core.firebase import db
from job_mail_automation.services.mail.gmail import GMAIL_SCOPES, Gmail
from job_mail_automation.types.user import User, UserOAuthCredentials

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

google_auth_router = Blueprint("google_auth_router", __name__)


@google_auth_router.get("/auth_url")
def url():
    mail = Gmail()
    auth_url = mail.get_oauth_authorization_url()

    return jsonify({"message": "success", "url": auth_url}), 200


@google_auth_router.get("/callback")
def callback():
    # OAuth client configuration in dictionary format
    client_config = {
        "web": {
            "client_id": GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    # Initiate the OAuth flow using the client config dictionary
    flow = Flow.from_client_config(
        client_config, GMAIL_SCOPES, redirect_uri=REDIRECT_URI
    )
    try:
        flow.fetch_token(authorization_response=request.url)
    except:
        return (
            jsonify(
                {"message": "internal_server_error", "reason": "OAuth token expired"}
            ),
            500,
        )

    id_info = id_token.verify_oauth2_token(
        flow.credentials.id_token,  # type: ignore
        google_requests.Request(),
        GOOGLE_OAUTH_CLIENT_ID,
    )

    user = (
        db.collection("users")
        .where(filter=FieldFilter("email", "==", id_info.get("email")))
        .get()
    )

    if not len(user):
        user = User.create(
            id_info.get("email"), id_info.get("name"), id_info.get("picture")
        )
    else:
        user = User.model_validate(user[0].to_dict())

    token, refresh_token = flow.credentials.token, flow.credentials.refresh_token
    user.update_oauth(UserOAuthCredentials(token=token, refresh_token=refresh_token))  # type: ignore

    return jsonify({"message": "success"}), 200
