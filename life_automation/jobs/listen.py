import threading
from concurrent.futures import ThreadPoolExecutor

from google.cloud.firestore_v1.base_query import FieldFilter

from life_automation.core.firebase import (
    EMAIL_JOBS_COLLECTION,
    PUBLISHING_JOBS_COLLECTION,
)
from life_automation.jobs.email_job.handler import handle_email_job
from life_automation.jobs.publishing_job.handler import handle_publishing_job
from life_automation.jobs.queue import JobQueue
from life_automation.types.job.email_job import EmailJob
from life_automation.types.job.publishing_job import PublishingJob

# Create a thread pool
thread_pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="job-worker")


def on_snapshot_email_jobs(snapshot, _, __):
    try:
        jobs = [EmailJob.model_validate(doc.to_dict()) for doc in snapshot]  # type: ignore
        if not jobs:
            return

        job_count = f"{len(jobs)} job{'s' if len(jobs) > 1 else ''}"
        job_desc = ", ".join([f"{job.id} ({job.task})" for job in jobs])

        JobQueue.dispatch_many(thread_pool, jobs, handle_email_job)
        print(f"✅ Dispatched {job_count}: {job_desc}")
    except KeyboardInterrupt:
        print("\n🛑 Exiting")


def on_snapshot_publishing_jobs(snapshot, _, __):
    try:
        jobs = [PublishingJob.model_validate(doc.to_dict()) for doc in snapshot]  # type: ignore
        if not jobs:
            return

        job_count = f"{len(jobs)} job{'s' if len(jobs) > 1 else ''}"
        job_desc = ", ".join([f"{job.id} ({job.task})" for job in jobs])

        JobQueue.dispatch_many(thread_pool, jobs, handle_publishing_job)
        print(f"✅ Dispatched {job_count}: {job_desc}")
    except KeyboardInterrupt:
        print("\n🛑 Exiting")


def listen_for_jobs():
    print("🚀 Listening for jobs")

    # Listen for changes in the email jobs collection
    EMAIL_JOBS_COLLECTION.where(
        filter=FieldFilter("status", "==", "WAITING")
    ).on_snapshot(on_snapshot_email_jobs)

    # Listen for changes in the publishing jobs collection
    PUBLISHING_JOBS_COLLECTION.where(
        filter=FieldFilter("status", "==", "WAITING")
    ).on_snapshot(on_snapshot_publishing_jobs)

    # Keep the thread alive
    threading.Event().wait()
