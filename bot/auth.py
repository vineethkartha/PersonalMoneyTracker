# bot/auth.py
import os

def get_allowed_users():
    print("DEBUG ENV: ", os.environ.get("ALLOWED_USER_IDS"))
    allowed_user_ids_str = os.getenv("ALLOWED_USER_IDS", "").strip()
    print("DEBUG: ",allowed_user_ids_str)
    if not allowed_user_ids_str:
        return set()

    return set(map(int, allowed_user_ids_str.split(",")))

ALLOWED_USERS = get_allowed_users()
