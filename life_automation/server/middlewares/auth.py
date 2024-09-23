from functools import wraps

from flask import jsonify, request

from life_automation.core.firebase import auth
from life_automation.types.user import User


def _handle_preflight():
    response = jsonify({"message": "CORS preflight"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Authorization, Content-Type",
    )
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


def _extract_firebase_token():
    firebase_auth_token = request.headers.get("Authorization")
    if not firebase_auth_token:
        return None
    return firebase_auth_token.replace("Bearer ", "")


def _fetch_user_from_firebase_token(firebase_auth_token) -> User | None:
    try:
        user = auth.verify_id_token(firebase_auth_token)
        user_email = user["email"]

        user = User.get_from_email(user_email)
        return user
    except Exception:
        print("Rejected request with invalid Firebase token or user not found")

    return None


def firebase_auth_middleware():
    if request.method == "OPTIONS":
        return _handle_preflight()

    firebase_auth_token = _extract_firebase_token()
    if not firebase_auth_token:
        return jsonify({"message": "unauthorized"}), 401

    user = _fetch_user_from_firebase_token(firebase_auth_token)
    if not user:
        return jsonify({"message": "unauthorized"}), 401

    setattr(request, "user", user)

    return None


def firebase_auth_middleware_wrapped(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = firebase_auth_middleware()
        if response is not None:
            return response

        return func(*args, **kwargs)

    return wrapper
