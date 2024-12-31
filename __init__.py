import os
import json
import pathlib
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, abort, session, url_for

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

load_dotenv(override=True)


app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")


# --- Setup Google OAuth ---
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
    print(f"all info from user ---> \n{id_info}\n")
    session["google_id"] = id_info.get("sub")
    session["email"] = id_info.get("email")
    session["name"] = id_info.get("name")
    session["google_profile_picture"] = id_info.get("picture")
    print("FLASK_SERVER: /login_with_google successful, checking if email is stored in 'users' collection")
    print(f"google_id = {session["google_id"]}")
    print(f"email = {session["email"]}")
    print(f"name = {session["name"]}")

    endpoint_url = f"{api_url}/check_if_exists/{session["email"]}"
    print(f"FLASK_SERVER: sending request - {endpoint_url}")

    try:
        response = requests.get(endpoint_url)
        data = response.json() 


        # TODO when a user creates an account without google, then decides to log in with google, 
        # store the google_id in mongoDB users collection
        print(f"response: {data}")
        if data["exists"] == "True": 
            print("User exists, redirecting to home")
            session["id"] = data["id"]
            return redirect("/home")
        else:
            print("User does not exist, redirecting to register")
            return redirect("/register_with_google")
    except Exception as e:
        print(f"Error: {e}")


    print("Logged in with Google, redirected to home")
    return redirect("/home")


@app.route('/login_with_google')
def login_with_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    print(f"STATE: {state}")
    return redirect(authorization_url)

@app.route("/register_with_google")
def register_with_google():
    # get name and email from session, these are added to input boxes for
    name = session["name"]
    email = session["email"]
    google_id = session["google_id"]
    profile_picture = session["google_profile_picture"]
    
    # if name and email are provided, redirect directly to /register
    return redirect(url_for("register", name=name, email=email, google_id=google_id, profile_picture=profile_picture))
# --- end of Google OAuth ---



@app.route('/')
def index():
    #if "google_id" in session:
     #   return redirect('home.html')
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    name = request.args.get("name", "")
    email = request.args.get("email", "")
    google_id = request.args.get("google_id", "")
    profile_picture = request.args.get("profile_picture", "default") # if default passed to endpoint then the default profile picture will be stored with the user

    return render_template("register.html", name=name, email=email, google_id=google_id, profile_picture=profile_picture)


@app.route('/login_with_email/<user_id>', methods=["GET"])
def login_with_email(user_id):
    session["id"] = user_id
    print(f"User logged in with ID: {user_id}")

    return redirect("/home")


@app.route("/home")
def home():
    return render_template('home.html', id=session["id"])

@app.route("/logout", methods=["GET"])
def logout():
    try:
        print(f" \n\n\n\nTrying to logout with id-{session['id']}")
        response = requests.post(f"{api_url}/logout/{session['id']}")
        data = response.json()
        print(f"response from logout: {data}")

        if response.status_code == 200:
            data = response.json()
            if data["logout"] == "True":
                print(f"FLASK SERVER: LOGGING OUT USER {id}")
                session.clear()
                return redirect("/")
            else:
                print(f"FLASK SERVER: ** FAILED ** LOGGING OUT USER {id}")
    except Exception as e:
        print(f"Error logging out: {e}")

if __name__ == "__main__":
    app.run(debug=True)