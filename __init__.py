from flask import Flask, render_template, redirect, request

from . import db

app = Flask(__name__)

@app.route('/')
def index():
    # if jwt is not valid return login page
    # if jwt is valid return index
    return render_template('index.html')

@app.route('/login', methods=["GET","POST"])
def login():
    username_db = "luke"
    password_db = "123"
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == username_db and password == password_db:
     
            return redirect('home')  
        else:
            print("Invalid details")

    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == "__main__":

    app.run()
