import os
import threading

from .core.firebase import setup_sample_db
from .jobs.listen import listen_for_jobs
from .server.server import start_server

os.system("clear")


def main():
    # setup_sample_db()

    threading.Thread(target=listen_for_jobs, daemon=True).start()
    start_server()
