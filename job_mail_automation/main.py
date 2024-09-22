import os
import threading

from google.cloud.firestore_v1.base_query import FieldFilter

from .core.firebase import db, setup_sample_db
from .core.job_queue import JobQueue
from .server.server import start_server
from .types.job import Job

os.system("clear")


def listen_for_jobs():
    print("🚀 Listening for jobs")

    def on_snapshot(snapshot, _, __):
        try:
            jobs = [Job.model_validate(doc.to_dict()) for doc in snapshot]  # type: ignore
            if jobs:
                print(f"⏰ {len(jobs)} jobs found. Dispatching...")
                JobQueue.dispatch_many(jobs)
        except KeyboardInterrupt:
            print("\n🛑 Exiting")

    query = db.collection("jobs").where(filter=FieldFilter("status", "==", "WAITING"))
    query.on_snapshot(on_snapshot)


def main():
    # setup_sample_db()

    threading.Thread(target=listen_for_jobs, daemon=True).start()
    start_server()
