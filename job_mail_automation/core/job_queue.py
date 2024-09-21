import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from job_mail_automation.core.firebase import db
from job_mail_automation.core.prompt_factory import PromptFactory
from job_mail_automation.services.llm.gpt4omini import GPT4oMini
from job_mail_automation.services.mail.gmail import Gmail
from job_mail_automation.types.job import Job
from job_mail_automation.types.user import User, UserOAuthCredentials


def _update_job_status(
    job_id: str, status: str, result: Any, system_message: str | None
):
    db.collection("jobs").document(job_id).update(
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
            db.collection("users").document(job.user_id).get().to_dict()
        )
    except Exception as e:
        raise Exception(f"Failed to fetch user details: {e}")

    # Step 2: Prepare email
    prompt = PromptFactory.make_email_write_prompt(
        # User details
        self_description=user.self_description,
        sample_email=user.sample_email,
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
    try:
        res = llm.run(prompt)
        if res is None:
            return "", ""
        res = json.loads(res)

        return res["subject"].strip(), res["body"].strip()
    except Exception as e:
        raise Exception(f"LLM failed with exception: {e}")


def send_email(job: Job):
    if not job.result:
        raise Exception("No email content provided")

    # Step 1: Generate prompt
    try:
        user = User.model_validate(
            db.collection("users").document(job.user_id).get().to_dict()
        )
        oauth_credentials = user.oauth_credentials
        if oauth_credentials is None:
            raise ValueError("Not authenticated with the mail service yet")
    except Exception as e:
        raise Exception(f"Failed to fetch user details: {e}")

    # Step 2: Prepare user's OAuth credentials
    try:
        credentials = Credentials(
            token=oauth_credentials.token,
            refresh_token=oauth_credentials.refresh_token,
        )
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            oauth_credentials = UserOAuthCredentials(
                token=credentials.token,
                refresh_token=credentials.refresh_token,
            )
            user.update_oauth(oauth_credentials)
    except:
        raise Exception("Mail server's credentials expired. Reauthentication required.")

    # Step 3: Send email
    mail = Gmail()
    mail.send(
        credentials=credentials,
        to_email=job.details.target_person_email,
        subject=job.result.subject,
        html_body=job.result.body,
        attachments=[],
    )

    # Step 4: Update the job
    db.collection("jobs").document(job.id).update(
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
    def dispatch_many(jobs: list[Job]):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(JobQueue.dispatch, job) for job in jobs]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Job failed with exception: {e}")