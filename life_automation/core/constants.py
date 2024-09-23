import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------------------
# General
# ---------------------------------------------------------------------------------------

MEDIUM_API_BASE_URI = "https://api.medium.com/v1"

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "*.yogeshaggarwal.in",
    "*.vercel.app",
    "*.web.app",
]

POLL_INTERVAL_IN_SECONDS = 10

# ---------------------------------------------------------------------------------------
# Gen AI
# ---------------------------------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY is not None, "Please set the OPENAI_API_KEY environment variable."

HF_API_KEY = os.getenv("HF_API_KEY")
assert HF_API_KEY is not None, "Please set the HF_API_KEY environment variable."

# ---------------------------------------------------------------------------------------
# Google
# ---------------------------------------------------------------------------------------

GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
assert (
    GOOGLE_OAUTH_CLIENT_ID is not None
), "Please set the GOOGLE_OAUTH_CLIENT_ID environment variable."

GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
assert (
    GOOGLE_OAUTH_CLIENT_SECRET is not None
), "Please set the GOOGLE_OAUTH_CLIENT_SECRET environment variable."

GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
assert (
    GOOGLE_OAUTH_REDIRECT_URI is not None
), "Please set the GOOGLE_OAUTH_REDIRECT_URI environment variable."

# ---------------------------------------------------------------------------------------
# Medium
# ---------------------------------------------------------------------------------------

MEDIUM_OAUTH_CLIENT_ID = os.getenv("MEDIUM_OAUTH_CLIENT_ID")
assert (
    MEDIUM_OAUTH_CLIENT_ID is not None
), "Please set the MEDIUM_OAUTH_CLIENT_ID environment variable."

MEDIUM_OAUTH_CLIENT_SECRET = os.getenv("MEDIUM_OAUTH_CLIENT_SECRET")
assert (
    MEDIUM_OAUTH_CLIENT_SECRET is not None
), "Please set the MEDIUM_OAUTH_CLIENT_SECRET environment variable."

MEDIUM_OAUTH_REDIRECT_URI = os.getenv("MEDIUM_OAUTH_REDIRECT_URI")
assert (
    MEDIUM_OAUTH_REDIRECT_URI is not None
), "Please set the MEDIUM_OAUTH_REDIRECT_URI environment variable."

# ---------------------------------------------------------------------------------------
