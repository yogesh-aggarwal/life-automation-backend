from google.cloud.firestore import CollectionReference


class JobContext:
    job_id: str
    db_collection_ref: CollectionReference
