import json
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from life_automation.core.firebase import JOBS_COLLECTION, USERS_COLLECTION
from life_automation.core.prompt_factory import PromptFactory
from life_automation.services.llm.gpt4omini import GPT4oMini
from life_automation.services.mail.gmail import Gmail
from life_automation.types.job import Job
from life_automation.types.user import User, UserOAuthCredentials


def _update_job_status(
    job_id: str, status: str, result: Any, system_message: str | None
):
    JOBS_COLLECTION.document(job_id).update(
        {
            "dateUpdated": int(time.time() * 1000),
            "status": status,
            "result": result,
            "systemMessage": system_message,
        }
    )


def _attempt_job(func):
    @wraps(func)
    def wrapper(job: Job, *args, **kwargs):
        result = None
        if job.result:
            result = job.result.model_dump(by_alias=True)
        _update_job_status(job.id, "WORKING", result, None)
        try:
            result = func(job, *args, **kwargs)
            _update_job_status(job.id, "COMPLETED", result, None)
        except Exception as e:
            print(e)
            _update_job_status(job.id, "FAILED", result, str(e))

    return wrapper


def generate_email_content(job: Job):
    llm = GPT4oMini()

    # Step 1: Get user details
    try:
        user = User.model_validate(
            USERS_COLLECTION.document(job.user_id).get().to_dict()
        )
    except Exception as e:
        raise Exception(f"Failed to fetch user details: {e}")

    # Step 2: Prepare email
    prompt = PromptFactory.make_email_write_prompt(
        # User details
        self_description=user.data.self_description,
        sample_email=user.data.sample_email,
        # Company details
        target_company_name=job.details.target_company_name,
        # Job details
        target_job_id=job.details.target_job_id,
        target_job_link=job.details.target_job_link,
        target_job_title=job.details.target_job_title,
        target_job_description=job.details.target_job_description,
        # Prospect details
        target_person_name=job.details.target_person_name,
        target_person_position=job.details.target_person_position,
        target_person_linkedin_profile_content=job.details.target_person_linkedin_profile_content,
    )
    for _ in range(5):
        try:
            res = llm.run(prompt)
            if res is None:
                raise Exception("LLM failed to generate content")
            res = json.loads(res)

            return res["subject"].strip(), res["body"].strip()
        except Exception as e:
            print(f"LLM failed with exception: {e}")

    raise Exception("LLM failed to generate content")


def send_email(job: Job):
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
    JOBS_COLLECTION.document(job.id).update(
        {
            "dateEmailSent": int(time.time() * 1000),
        }
    )


class JobQueue:
    @staticmethod
    @_attempt_job
    def dispatch(job: Job) -> dict[str, Any] | None:
        if job.task == "GENERATE_EMAIL":
            subject, body = generate_email_content(job)
            return {"subject": subject, "body": body}
        elif job.task == "SEND_EMAIL":
            if not job.result:
                raise Exception("No email content provided")
            send_email(job)
            return job.result.model_dump(by_alias=True)

        return None

    @staticmethod
    def dispatch_many(thread_pool: ThreadPoolExecutor, jobs: list[Job]):
        for job in jobs:
            thread_pool.submit(JobQueue.dispatch, job)
