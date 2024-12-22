import os
import json
import pathlib
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, abort, session

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

load_dotenv(override=True)


app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")


# --- Setup Google OAuth
GOOGLE_CLIENT_ID = (os.getenv("GOOGLE_CLIENT_ID"))
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, ".client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri = "https://oscarwatch.online/callback",
)

api_url = "https://api.oscarwatch.online/api"

def login_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper

@app.route('/')
def index():
    #if "google_id" in session:
     #   return redirect('home.html')
    return render_template("index.html")

@app.route('/login_with_google')
def login_with_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route('/login_with_email')
def login_with_email():
    print("Logged in with email, redirecting to home")
    return redirect("/home")

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session.get("state") == request.args.get("state"):
        abort(500)  # States don't match

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["email"] = id_info.get("email")
    session["name"] = id_info.get("name")

    print(f"google_id = {session["google_id"]}")
    print(f"email = {session["email"]}")
    print(f"name = {session["name"]}")

    # 
    endpoint_url = f"{api_url}/google/{session["google_id"]}"
    try:
        response = requests.get(endpoint_url)
        data = response.json() 
        print(data)
        if data["exists"] == True: 
            print("User exists, redirecting to home")
            return redirect("/home")
        else:
            print("User does not exist, redirecting to register")
            return redirect("/register")
    except Exception as e:
        print(f"Error: {e}")


    print("Logged in with Google, redirected to home")
    return redirect("/home")

@app.route("/register_with_email")
def register_with_email():
    print("Registered with email, redirected to home")
    return redirect("/home")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




# Page routes
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    #print("From register router:" + session["google_id"])
    return render_template('register.html')


@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == "__main__":

    app.run(host="192.168.1.150", port=8080, debug=True)