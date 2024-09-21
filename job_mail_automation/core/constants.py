import os

from dotenv import load_dotenv

load_dotenv()

POLL_INTERVAL_IN_SECONDS = 10

REDIRECT_URI = os.getenv("REDIRECT_URI")
assert REDIRECT_URI is not None, "Please set the REDIRECT_URI environment variable."

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY is not None, "Please set the OPENAI_API_KEY environment variable."

HF_API_KEY = os.getenv("HF_API_KEY")
assert HF_API_KEY is not None, "Please set the HF_API_KEY environment variable."

GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
assert (
    GOOGLE_OAUTH_CLIENT_ID is not None
), "Please set the GOOGLE_OAUTH_CLIENT_ID environment variable."

GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
assert (
    GOOGLE_OAUTH_CLIENT_SECRET is not None
), "Please set the GOOGLE_OAUTH_CLIENT_SECRET environment variable."
