import requests

from life_automation.core.constants import (
    MEDIUM_API_BASE_URI,
    MEDIUM_OAUTH_CLIENT_ID,
    MEDIUM_OAUTH_CLIENT_SECRET,
)
from life_automation.core.firebase import USERS_COLLECTION
from life_automation.types.job.publishing_job import PublishingJob
from life_automation.types.user import User, UserOAuthCredentials


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

    @staticmethod
    def publish_and_get_url(
        access_token: str, user_id: str, job: PublishingJob
    ) -> str | None:
        try:
            response = requests.post(
                f"{MEDIUM_API_BASE_URI}/users/{user_id}/posts",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Accept-Charset": "utf-8",
                },
                json={
                    "title": job.details.title,
                    "content": job.details.content,
                    "tags": job.details.tags,
                    "canonicalUrl": job.details.canonical_url,
                    "publishStatus": job.details.visibility,
                    "contentFormat": "markdown",
                },
            )
            response.raise_for_status()

            post_url = response.json()["data"]["url"]
            return post_url
        except Exception as e:
            print("Error:", e)

        return None


def publish_task(job: PublishingJob) -> str | None:
    # Step 1: Get the user
    try:
        user = User.model_validate(
            USERS_COLLECTION.document(job.user_id).get().to_dict()
        )
    except Exception as e:
        raise Exception(f"Failed to fetch user details: {e}")

    # Step 2: Get user ID from the access token and renew the token if necessary
    oauth_creds = user.credentials.medium_oauth
    if oauth_creds is None:
        raise RuntimeError("User has not connected their Medium account")
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
        except Exception:
            raise RuntimeError("User has not connected their Medium account")

    # Step 3: Prepare the request body
    post_url = Helpers.publish_and_get_url(access_token, str(medium_user_id), job)
    if post_url is None:
        raise Exception("Failed to publish the post")

    return post_url
