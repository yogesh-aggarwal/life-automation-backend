import requests
from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field

from job_mail_automation.types.user import User

medium_router = Blueprint("medium_router", __name__)

API_BASE_URI = "https://api.medium.com/v1"


class Helpers:
    @staticmethod
    def get_user_id(access_token: str) -> str | None:
        try:
            # Send the GET request
            response = requests.get(
                f"{API_BASE_URI}/me",
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

    # Step 1: Get user ID from the access token
    user: User = getattr(request, "user")
    oauth_creds = user.credentials.medium_oauth
    if oauth_creds is None:
        return jsonify({"message": "unauthorized"}), 401
    access_token = oauth_creds.access_token

    user_id = Helpers.get_user_id(access_token)
    if user_id is None:
        return jsonify({"message": "unauthorized"}), 401

    # Step 2: Prepare the request body
    try:
        response = requests.post(
            f"{API_BASE_URI}/users/{user_id}/posts",
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
