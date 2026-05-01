import streamlit_authenticator as stauth

def get_authenticator():
    credentials = {
        "usernames": {
            "admin": {"name": "管理者", "password": "concrete2026"},
            "user01": {"name": "テストユーザー", "password": "guest456"}
        }
    }
    return stauth.Authenticate(credentials, "concrete_quiz_cookie", "auth_key", cookie_expiry_days=30)