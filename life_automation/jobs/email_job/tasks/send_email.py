import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from life_automation.core.firebase import EMAIL_JOBS_COLLECTION, USERS_COLLECTION
from life_automation.services.mail.gmail import Gmail
from life_automation.types.job.email_job import EmailJob
from life_automation.types.user import User, UserOAuthCredentials


def send_email_task(job: EmailJob):
    if not job.result:
        raise Exception("No email content provided")

    # Step 1: Generate prompt
    try:
        user = User.model_validate(
            USERS_COLLECTION.document(job.user_id).get().to_dict()
        )
        oauth_credentials = user.credentials.google_oauth
        if oauth_credentials is None:
            raise ValueError("Not authenticated with the mail service yet")
    except Exception as e:
        raise Exception(f"Failed to fetch user details: {e}")

    # Step 2: Prepare user's OAuth credentials
    try:
        credentials = Credentials(
            token=oauth_credentials.access_token,
            refresh_token=oauth_credentials.refresh_token,
        )
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            oauth_credentials = UserOAuthCredentials(
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
            )
            user.update_creds_google_oauth(oauth_credentials)
    except:
        user.update_creds_google_oauth(None)
        raise Exception("Mail server's credentials expired. Reauthentication required.")

    # Step 3: Send email
    try:
        mail = Gmail()
        mail.send(
            credentials=credentials,
            to_email=job.details.target_person_email,
            subject=job.result.subject,
            html_body=job.result.body,
            attachments=[job.details.resume_url],
        )
    except Exception as e:
        user.update_creds_google_oauth(None)
        raise Exception(f"Failed to send email: {e}")

    # Step 4: Update the job
    EMAIL_JOBS_COLLECTION.document(job.id).update(
        {
            "dateEmailSent": int(time.time() * 1000),
        }
    )
