import streamlit_authenticator as stauth

passwords = ["YourPasswordHere"]
hashes = stauth.Hasher(passwords).generate()

for p, h in zip(passwords, hashes):
    print(p, "->", h)
