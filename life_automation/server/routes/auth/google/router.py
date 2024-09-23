import os

from flask import Blueprint, jsonify, request
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from life_automation.core.constants import (
    GOOGLE_OAUTH_CLIENT_ID,
    GOOGLE_OAUTH_CLIENT_SECRET,
    GOOGLE_OAUTH_REDIRECT_URI,
)
from life_automation.services.mail.gmail import GMAIL_SCOPES, Gmail
from life_automation.types.user import User, UserOAuthCredentials

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
            "redirect_uris": [GOOGLE_OAUTH_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    # Initiate the OAuth flow using the client config dictionary
    flow = Flow.from_client_config(
        client_config, GMAIL_SCOPES, redirect_uri=GOOGLE_OAUTH_REDIRECT_URI
    )
    try:
        flow.fetch_token(authorization_response=request.url)
    except:
        return (
            jsonify(
                {
                    "message": "internal_server_error",
                    "reason": "OAuth token expired",
                }
            ),
            500,
        )

    id_info = id_token.verify_oauth2_token(
        flow.credentials.id_token,  # type: ignore
        google_requests.Request(),
        GOOGLE_OAUTH_CLIENT_ID,
    )
    user_email = id_info.get("email")

    try:
        user = User.get_from_email(user_email)
    except Exception:
        return jsonify({"message": "user_not_found"}), 404

    access_token, refresh_token = flow.credentials.token, flow.credentials.refresh_token
    user.update_creds_google_oauth(UserOAuthCredentials(access_token=access_token, refresh_token=refresh_token))  # type: ignore

    return jsonify({"message": "success"}), 200
