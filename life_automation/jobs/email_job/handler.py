from typing import Any

from life_automation.types.job.email_job import EmailJob

from .tasks.generate_email import generate_email_task
from .tasks.send_email import send_email_task


def handle_email_job(job: EmailJob) -> dict[str, Any] | None:
    if job.task == "GENERATE_EMAIL":
        subject, body = generate_email_task(job)
        return {"subject": subject, "body": body}
    elif job.task == "SEND_EMAIL":
        send_email_task(job)
        # This job will always be triggered by a previous job, so it will always have a result
        return job.result.model_dump(by_alias=True)  # type: ignore

    return None
