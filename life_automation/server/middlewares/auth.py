from flask import request, jsonify

from life_automation.core.firebase import auth
from life_automation.types.user import User


def firebase_auth_middleware():
    firebase_auth_token = request.headers.get("Firebase-Authorization-Token")
    if not firebase_auth_token:
        return jsonify({"message": "unauthorized"}), 401

    try:
        user = auth.verify_id_token(firebase_auth_token)
        user_email = user["email"]

        try:
            user = User.get_from_email(user_email)
        except Exception:
            return jsonify({"message": "user_not_found"}), 404

        setattr(request, "user", user)
    except Exception:
        print("Rejected request with invalid Firebase token")
        return jsonify({"message": "unauthorized"}), 401

    return None
