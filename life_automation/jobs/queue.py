import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar

from life_automation.types.context.job import JobContext
from life_automation.types.job.email_job import EmailJob
from life_automation.types.job.publishing_job import PublishingJob

T = TypeVar("T")
JobHandler = Callable[[T], dict[str, Any] | None]
GenericJob = EmailJob | PublishingJob


def _update_job_status(
    ctx: JobContext,
    status: str,
    result: Any,
    system_message: str | None,
):
    ctx.db_collection_ref.document(ctx.job_id).update(
        {
            "dateUpdated": int(time.time() * 1000),
            "status": status,
            "result": result,
            "systemMessage": system_message,
        }
    )


class JobQueue:
    @staticmethod
    def dispatch[
        JobType: GenericJob
    ](ctx: JobContext, job: JobType, handler: JobHandler[JobType]):
        result = None
        if job.result:
            result = job.result.model_dump(by_alias=True)

        _update_job_status(ctx, "WORKING", result, None)
        try:
            result = handler(job)
            _update_job_status(ctx, "COMPLETED", result, None)
        except Exception as e:
            print(e)
            _update_job_status(ctx, "FAILED", result, str(e))

    @staticmethod
    def dispatch_many[
        JobType: GenericJob
    ](
        thread_pool: ThreadPoolExecutor,
        jobs: list[tuple[JobContext, JobType]],
        handler: JobHandler[JobType],
    ):
        for ctx, job in jobs:
            thread_pool.submit(JobQueue.dispatch, ctx, job, handler)
