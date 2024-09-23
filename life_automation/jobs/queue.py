import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Callable, TypeVar

from life_automation.core.firebase import EMAIL_JOBS_COLLECTION
from life_automation.types.job.job import Job

T = TypeVar("T")
JobHandler = Callable[[T], dict[str, Any] | None]


def _update_job_status(
    job_id: str, status: str, result: Any, system_message: str | None
):
    EMAIL_JOBS_COLLECTION.document(job_id).update(
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


class JobQueue:
    @staticmethod
    @_attempt_job
    def dispatch[JobType](job: JobType, handler: JobHandler[JobType]):
        return handler(job)

    @staticmethod
    def dispatch_many[
        JobType
    ](
        thread_pool: ThreadPoolExecutor,
        jobs: list[JobType],
        handler: JobHandler[JobType],
    ):
        for job in jobs:
            thread_pool.submit(JobQueue.dispatch, job, handler)
