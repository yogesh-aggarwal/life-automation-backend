import os
import threading
from concurrent.futures import ThreadPoolExecutor

from google.cloud.firestore_v1.base_query import FieldFilter

from .core.firebase import JOBS_COLLECTION, setup_sample_db
from .core.job_queue import JobQueue
from .server.server import start_server
from .types.job import Job

os.system("clear")


def listen_for_jobs():
    print("🚀 Listening for jobs")

    # Create a thread pool
    thread_pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="job-worker")

    def on_snapshot(snapshot, _, __):
        try:
            jobs = [Job.model_validate(doc.to_dict()) for doc in snapshot]  # type: ignore
            if not jobs:
                return

            job_count = f"{len(jobs)} job{'s' if len(jobs) > 1 else ''}"
            job_desc = ", ".join([f"{job.id} ({job.task})" for job in jobs])

            JobQueue.dispatch_many(thread_pool, jobs)
            print(f"✅ Dispatched {job_count}: {job_desc}")
        except KeyboardInterrupt:
            print("\n🛑 Exiting")

    query = JOBS_COLLECTION.where(filter=FieldFilter("status", "==", "WAITING"))
    query.on_snapshot(on_snapshot)

    # Keep the thread alive
    threading.Event().wait()


def main():
    # setup_sample_db()

    threading.Thread(target=listen_for_jobs, daemon=True).start()
    start_server()
