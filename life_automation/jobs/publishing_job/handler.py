from typing import Any

from life_automation.types.job.publishing_job import PublishingJob

from .tasks.publish import publish_task


def handle_publishing_job(job: PublishingJob) -> dict[str, Any] | None:
    if job.task == "PUBLISH":
        url = publish_task(job)
        return {"url": url} if url else None

    return None
