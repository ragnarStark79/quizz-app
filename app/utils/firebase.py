from firebase_admin import auth


def verify_firebase_token(id_token):
    """
    Verify a Firebase ID token and return the decoded user data.
    Returns None if the token is invalid or expired.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        return None
