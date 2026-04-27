import streamlit_authenticator as stauth

# ここに購入者に発行したいパスワードを入れる
passwords = ['concrete2026', 'guest456']
hashed_passwords = stauth.Hasher(passwords).generate()

print(hashed_passwords)
