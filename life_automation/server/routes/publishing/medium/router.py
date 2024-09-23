import requests
from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field

from life_automation.core.constants import (
    MEDIUM_API_BASE_URI,
    MEDIUM_OAUTH_CLIENT_ID,
    MEDIUM_OAUTH_CLIENT_SECRET,
)
from life_automation.types.user import User, UserOAuthCredentials

medium_router = Blueprint("medium_router", __name__)


class Helpers:
    @staticmethod
    def renew_access_token(refresh_token: str) -> str | None:
        try:
            response = requests.post(
                f"{MEDIUM_API_BASE_URI}/tokens",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "Accept-Charset": "utf-8",
                },
                data={
                    "refresh_token": refresh_token,
                    "client_id": MEDIUM_OAUTH_CLIENT_ID,
                    "client_secret": MEDIUM_OAUTH_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()

            return response.json()["access_token"]
        except Exception as e:
            print("Error:", e)

        return None

    @staticmethod
    def get_user_id(access_token: str) -> str | None:
        try:
            # Send the GET request
            response = requests.get(
                f"{MEDIUM_API_BASE_URI}/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Accept-Charset": "utf-8",
                },
            )
            response.raise_for_status()

            # Extract the user ID
            user_id = response.json()["data"]["id"]

            return user_id
        except Exception as e:
            print("Error:", e)

        return None


class PublishRequest(BaseModel):
    title: str = Field(..., title="Title of the post")
    content: str = Field(..., title="Markdown content of the post")
    tags: list[str] = Field([], title="Tags for the post")
    canonical_url: str = Field(None, title="Canonical URL of the post")
    visibility: str = Field("public", title="Visibility of the post")


@medium_router.post("/publish")
def publish():
    try:
        body = PublishRequest.model_validate(request.json)
    except Exception as e:
        return jsonify({"message": "invalid_body_content"}), 400

    # Step 1: Get user ID from the access token and renew the token if necessary
    user: User = getattr(request, "user")
    oauth_creds = user.credentials.medium_oauth
    if oauth_creds is None:
        return jsonify({"message": "unauthorized"}), 401
    access_token, refresh_token = oauth_creds.access_token, oauth_creds.refresh_token

    for _ in range(2):
        try:
            medium_user_id = Helpers.get_user_id(access_token)
            if medium_user_id is None:
                # Renew the access token
                access_token = Helpers.renew_access_token(refresh_token)
                if access_token is None:
                    user.update_creds_medium_oauth(None)
                    raise Exception("Failed to renew the access token")
                else:
                    user.update_creds_medium_oauth(
                        UserOAuthCredentials(
                            access_token=access_token,
                            refresh_token=refresh_token,
                        )
                    )
        except Exception as e:
            return jsonify({"message": "auth_expired"}), 401

    # Step 2: Prepare the request body
    try:
        response = requests.post(
            f"{MEDIUM_API_BASE_URI}/users/{medium_user_id}/posts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Charset": "utf-8",
            },
            json={
                "title": body.title,
                "content": body.content,
                "tags": body.tags,
                "canonicalUrl": body.canonical_url,
                "publishStatus": body.visibility,
                "contentFormat": "markdown",
            },
        )
        response.raise_for_status()

        post_url = response.json()["data"]["url"]

        return jsonify({"message": "success", "url": post_url}), 200
    except Exception as e:
        print("Error:", e)

    return jsonify({"message": "internal_server_error"}), 500
