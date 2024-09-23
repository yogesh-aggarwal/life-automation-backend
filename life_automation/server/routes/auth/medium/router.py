from urllib.parse import urlencode

import requests
from flask import Blueprint, jsonify, request

from life_automation.core.constants import (
    MEDIUM_OAUTH_CLIENT_ID,
    MEDIUM_OAUTH_CLIENT_SECRET,
    MEDIUM_OAUTH_REDIRECT_URI,
)
from life_automation.server.middlewares.auth import firebase_auth_middleware
from life_automation.types.user import User, UserOAuthCredentials

medium_auth_router = Blueprint("medium_auth_router", __name__)

medium_auth_router.before_request(firebase_auth_middleware)


@medium_auth_router.get("/auth_url")
def auth_url():
    user: User = getattr(request, "user")
    query_params = urlencode(
        {
            "state": user.email,
            "response_type": "code",
            "scope": "basicProfile,publishPost",
            "client_id": MEDIUM_OAUTH_CLIENT_ID,
            "redirect_uri": MEDIUM_OAUTH_REDIRECT_URI,
        }
    )
    url = f"https://medium.com/m/oauth/authorize?{query_params}"

    print(url)

    return jsonify({"message": "success", "url": url}), 200


@medium_auth_router.get("/callback")
def callback():
    code = request.args.get("code")
    user_email = request.args.get("state")
    if not code or not user_email:
        return jsonify({"message": "bad_request"}), 400

    # Step 1: Get the user
    try:
        user = User.get_from_email(user_email)
    except Exception:
        return jsonify({"message": "user_not_found"}), 404

    # Step 2: Gather access token and refresh token
    try:
        response = requests.post(
            "https://api.medium.com/v1/tokens",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Accept-Charset": "utf-8",
            },
            data={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": MEDIUM_OAUTH_CLIENT_ID,
                "client_secret": MEDIUM_OAUTH_CLIENT_SECRET,
                "redirect_uri": MEDIUM_OAUTH_REDIRECT_URI,
            },
        )
        response.raise_for_status()

        access_token, refresh_token = (
            response.json()["access_token"],
            response.json()["refresh_token"],
        )
    except Exception:
        return jsonify({"message": "internal_server_error"}), 500

    # Step 3: Update the user's credentials
    user.update_creds_medium_oauth(
        UserOAuthCredentials(access_token=access_token, refresh_token=refresh_token)
    )

    return jsonify({"message": "success"}), 200
