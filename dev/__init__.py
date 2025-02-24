import os
import time
import json
import pathlib
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, abort, session, url_for, jsonify

# for file upload
from werkzeug.utils import secure_filename

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

import boto3


load_dotenv(override=True)

alive = 0
active_users = 0
data = {}

# setup for audio file upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'webm'}


app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

app.config['UPLOAD_FOLDER'] = "/uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# check if the uploaded file extension is within the allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    redirect_uri = "https://0e0a-86-46-231-56.ngrok-free.app/callback",
)

api_url = "http://0.0.0.0:80/api"

def login_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper

@app.route("/callback")
def callback():
    global active_users

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
            active_users+=1
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
    return render_template("landing.html")

@app.route("/keep_alive")
def keep_alive():
    global alive, data, active_users
    alive += 1
    keep_alive_count = str(alive)
    data["keep_alive"] = keep_alive_count
    data["active_users"] = active_users
    parsed_json = json.dumps(data)
    print(parsed_json)
    return str(parsed_json)

@app.route("/register")
def register():
    name = request.args.get("name", "")
    email = request.args.get("email", "")
    google_id = request.args.get("google_id", "")
    profile_picture = request.args.get("profile_picture", "default") # if default passed to endpoint then the default profile picture will be stored with the user

    return render_template("register.html", name=name, email=email, google_id=google_id, profile_picture=profile_picture)

@app.route("/login")
def login():
    
    return render_template("login.html")


@app.route('/login_with_email/<user_id>', methods=["GET"])
def login_with_email(user_id):
    global active_users
    session["id"] = user_id
    print(f"User logged in with ID: {user_id}")
    active_users+=1

    return redirect("/home")



@app.route("/logout", methods=["GET"])
def logout():
    global active_users
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
                if active_users > 0:
                    active_users-=1
                return redirect("/")
            else:
                print(f"FLASK SERVER: ** FAILED ** LOGGING OUT USER {id}")
    except Exception as e:
        print(f"Error logging out: {e}")


# connects with boto3 to create clients giving me access to AWS Kinesis, i get the HLS URL for the live stream and pass it back to the
# front end to display, this will get called every 4-5 minutes as the HLS URL provided by AWS has a ttl of this time
def get_hls_url():
    kinesis_client = boto3.client(
    'kinesisvideo',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

    endpoint = kinesis_client.get_data_endpoint(
         StreamName = "OscarWatch_CAM01",
         APIName = "GET_HLS_STREAMING_SESSION_URL"
    )["DataEndpoint"]

    kv_access_manager = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint, region_name="eu-west-1")

    response = kv_access_manager.get_hls_streaming_session_url(
        StreamName = "OscarWatch_CAM01",
        PlaybackMode="LIVE"
    )
    url = response["HLSStreamingSessionURL"]
    url = url.strip()
    return url


@app.route("/home")
def home():
    # get a new hls url every time the route is called
    hls_url = get_hls_url()

    # fetch user details from database to pass into profile page
    endpoint_url = f"{api_url}/{session["id"]}"
    try:
        response = requests.get(endpoint_url)
        data = response.json() 
        print(f"HERE {data}")

    except Exception as e:
        print(f"Error: {e}")
    
    #TODO setup automatic calling everything 3 mins as the ttl of the url is 3 mins, video pauses once it dies
    print("Generated HLS URL:", hls_url)
    return render_template('home.html', id=session["id"], hls_url=hls_url, name=data["name"], profile=data["profile_picture"])

@app.route("/profile")
def profile():
    endpoint_url = f"{api_url}/{session["id"]}"
    # fetch user details from database to pass into profile page
    try:
        response = requests.get(endpoint_url)
        data = response.json() 
        print(f"DATA {data}")
    except Exception as e:
        print(f"Error: {e}")

    return render_template("profile-page.html", id=session["id"], name=data["name"], email=data["email"], profile=data["profile_picture"], date_joined=data["date_joined"], screenshots=data["screenshots"])



# --------- PubNub ---------

# this route returns the publish and subscribe keys to a function in my main.js. This allows me to hide my publish and subscribe keys in this file
@app.route("/get_pubnub_keys", methods=["GET"])
def get_pubnub_keys():
    return jsonify({
        "publishKey": os.getenv("PUBNUB_PUBLISH_KEY"),
        "subscribeKey": os.getenv("PUBNUB_SUBSCRIBE_KEY")
    })

# ------------------------



# uploading files with flask: https://flask.palletsprojects.com/en/stable/patterns/fileuploads/?utm_source=chatgpt.com
@app.route("/upload", methods=["POST", "GET"])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['audio']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == "__main__":
    app.run(debug=True)