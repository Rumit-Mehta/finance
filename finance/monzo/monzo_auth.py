import logging
from flask import Flask, redirect, request, session
from flask_session import Session
from finance import constants
import secrets
import requests
import os

app = Flask(__name__)
app.secret_key = constants.FLASK_SECRET

CLIENT_ID = constants.MONZO_CLIENT_ID
CLIENT_SECRET = constants.MONZO_CLIENT_SECRET
REDIRECT_URI = "http://localhost:5001/callback"

@app.route("/")
def authorize():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    session.modified = True

    auth_url = (
        f"https://auth.monzo.com/?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&state={state}"
    )
    logging.debug(
        f"\n🔗 Monzo OAuth URL: {auth_url}\n"
    )  # ✅ Add this line to output the full URL
    return redirect(auth_url)


@app.route("/callback")
def callback():
    print(f"Session at callback: {dict(session)}")
    print(f"Session cookie: {request.cookies.get('session')}")

    code = request.args.get("code")
    state = request.args.get("state")

    # temp fix - remove later
    if session.get("oauth_state") is None:
        logging.error("OAuth state not found in session!")

    if state != session.get("oauth_state") and session.get("oauth_state") is not None:
        return "Invalid state parameter", 400

    token_url = "https://api.monzo.com/oauth2/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    response = requests.post(token_url, data=payload)
    token_data = response.json()
    access_token = token_data.get("access_token")

    if access_token:
        os.makedirs("files", exist_ok=True)
        with open("files/monzo_access_token.txt", "w") as file:
            file.write(access_token)
        return "Access token saved successfully! - Open Monzo App"
    else:
        return f"Failed to get token: {response.text}", 400


if __name__ == "__main__":
    app.run(port=5001)
