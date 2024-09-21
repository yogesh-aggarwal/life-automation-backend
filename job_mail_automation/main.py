import os
import threading
import time

from google.cloud.firestore_v1.base_query import FieldFilter

from .core.constants import POLL_INTERVAL_IN_SECONDS
from .core.firebase import db, setup_sample_db
from .core.job_queue import JobQueue
from .server.server import start_server
from .types.job import Job

os.system("clear")


def update_platform_vitals():
    time_now_in_millis = int(time.time() * 1000)
    db.collection("platform").document("vitals").update(
        {
            "lastPoll": time_now_in_millis,
            "nextPoll": time_now_in_millis + POLL_INTERVAL_IN_SECONDS * 1000,
        }
    )


def listen_for_jobs():
    print("🚀 Listening for jobs")

    try:
        while True:
            snapshot = (
                db.collection("jobs")
                .where(filter=FieldFilter("status", "==", "WAITING"))
                .stream()
            )

            jobs = [Job.model_validate(doc.to_dict()) for doc in snapshot]  # type: ignore
            if jobs:
                print(f"⏰ {len(jobs)} jobs found. Dispatching...")
                JobQueue.dispatch_many(jobs)

            update_platform_vitals()

            print(f"🕒 Sleeping for {POLL_INTERVAL_IN_SECONDS} seconds.")
            time.sleep(POLL_INTERVAL_IN_SECONDS)
    except KeyboardInterrupt:
        print("\n🛑 Exiting")


def main():
    # setup_sample_db()

    threading.Thread(target=listen_for_jobs, daemon=True).start()
    start_server()
