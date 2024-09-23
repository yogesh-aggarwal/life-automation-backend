import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Callable, TypeVar

from google.cloud.firestore import CollectionReference

from life_automation.types.job.job import Job

T = TypeVar("T")
JobHandler = Callable[[T], dict[str, Any] | None]


def _update_job_status(
    collection_ref: CollectionReference,
    job_id: str,
    status: str,
    result: Any,
    system_message: str | None,
):
    collection_ref.document(job_id).update(
        {
            "dateUpdated": int(time.time() * 1000),
            "status": status,
            "result": result,
            "systemMessage": system_message,
        }
    )


def _attempt_job(func: Callable, collection_ref: CollectionReference):
    @wraps(func)
    def wrapper(job: Job, *args, **kwargs):
        result = None
        if job.result:
            result = job.result.model_dump(by_alias=True)
        _update_job_status(collection_ref, job.id, "WORKING", result, None)
        try:
            result = func(job, *args, **kwargs)
            _update_job_status(collection_ref, job.id, "COMPLETED", result, None)
        except Exception as e:
            print(e)
            _update_job_status(collection_ref, job.id, "FAILED", result, str(e))

    return wrapper


class JobQueue:
    @staticmethod
    def dispatch[
        JobType
    ](
        job: JobType,
        handler: JobHandler[JobType],
        db_collection_ref: CollectionReference,
    ):
        wrapped_handler = _attempt_job(handler, db_collection_ref)
        return wrapped_handler(job)  # type: ignore

    @staticmethod
    def dispatch_many[
        JobType
    ](
        thread_pool: ThreadPoolExecutor,
        jobs: list[JobType],
        handler: JobHandler[JobType],
        db_collection_ref: CollectionReference,
    ):
        for job in jobs:
            thread_pool.submit(JobQueue.dispatch, job, handler, db_collection_ref)
