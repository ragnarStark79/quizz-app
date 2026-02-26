import os
import json
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin only once
if not firebase_admin._apps:
    firebase_credentials = os.environ.get("FIREBASE_CREDENTIALS")

    if firebase_credentials:
        # Parse JSON string from environment variable
        cred_dict = json.loads(firebase_credentials)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

def verify_firebase_token(id_token):
    """
    Verify a Firebase ID token and return decoded user data.
    Returns None if token is invalid or expired.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        return None