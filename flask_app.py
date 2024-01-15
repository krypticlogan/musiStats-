import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template
import os
from dotenv import load_dotenv
import random as ran
import json
from flask_sqlalchemy import SQLAlchemy
import sshtunnel
from datetime import datetime
code = None
USERNAME = ''

def load(path=None, file=None):
    load_dotenv(path, file)

load()

#apis
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
spotify_scope = "user-read-recently-played"+"%20"+"user-top-read"+"%20"+"user-library-read"+"%20"+"user-read-currently-playing"
#redirect_uri='http://127.0.0.1:5000/stats/'
redirect_uri='https://www.musistats.net/stats'
##spotify auth
def spotify_auth():
    #redirect_uri=url_for('spotifyUserLogin',_external=True)
    sp = SpotifyOAuth(client_id =SPOTIFY_CLIENT_ID, client_secret = SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri, scope = spotify_scope)
    return sp

def generate_key():
    key = ''
    while (len(key) < 31):
        n = ran.randint(0,100)
        key = key + str(n)
    return key

#apis
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
spotify_scope = "user-read-recently-played"+"%20"+"user-top-read"+"%20"+"user-library-read"+"%20"+"user-read-currently-playing"
# redirect_uri='http://127.0.0.1:5000/stats'
state = generate_key()
redirect_uri='https://www.musistats.net/stats'
##spotify auth
def spotify_auth():
    #redirect_uri=url_for('spotifyUserLogin',_external=True)
    sp = spotipy.oauth2.SpotifyOAuth(client_id =SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET, redirect_uri=redirect_uri, scope = spotify_scope, state=state)
    return sp



    ##apple auth
def apple_auth():
    return


    ##soundcloud auth
def soundcloud_auth():
    return
##

def generate_key():
    key = ''
    while (len(key) < 31):
        n = ran.randint(0,100)
        key = key + str(n)
    return key

    #app
#app = Flask(__name__, template_folder='/home/loganj/musiStats/templateFiles',static_folder='static')
app = Flask(__name__, template_folder='templateFiles',static_folder='static')
app.secret_key = generate_key()
app.config['SESSION COOKIE NAME'] = 'cookie'
app.config['DEBUG'] = True

SSH_PASSWORD = os.environ.get('SSH_PASSWORD')

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="loganj",
    password="sqlroot",
    hostname="loganj.mysql.pythonanywhere-services.com",
    databasename="loganj$musiStats",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    created = db.Column(db.Date, default = datetime.utcnow)


@app.route('/')#home page
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/stats', methods=['GET'])
def stats():
    auth = SpotifyOAuth(client_id =SPOTIPY_CLIENT_ID,client_secret = SPOTIPY_CLIENT_SECRET , redirect_uri=redirect_uri, scope = spotify_scope, state=state)


    access_token = auth.get_cached_token()
    sp = spotipy.Spotify(auth_manager=auth)

    if access_token: #checks for access token

        result = sp.current_user() #gets the current user

        #parsing json data
        USERNAME = (result['display_name'])
        
    
        return render_template('tracks.html', username=USERNAME)
    
    else:
     code = request.args.get('code')
     auth.get_access_token(code, as_dict=False)
     

     return redirect("/tracks")
    
    

@app.route('/user')#for signed-in users
def user():
    auth = SpotifyOAuth(client_id =SPOTIPY_CLIENT_ID,client_secret = SPOTIPY_CLIENT_SECRET , redirect_uri=redirect_uri, scope = spotify_scope, state=state)
    sp = spotipy.Spotify(auth_manager=auth)

    access_token = auth.get_cached_token()
    if access_token: 

        result = sp.current_user()

        USERNAME = (result['display_name'])
        userImage = (result['images'][0]['url'])
    
        return render_template('user.html', username=USERNAME, userImage=userImage)
    
    else:
        return render_template('user.html')

    #redirects and authentications
@app.route('/sp', methods=['POST'])#for spotify sign-ups
def spotifyUserLogin():
    sp = spotify_auth()
    return redirect(os.environ.get('SPOTIFY_AUTH_URL')+'response_type=code&client_id='+sp.client_id+'&scope='+sp.scope+'&redirect_uri='+sp.redirect_uri)
    #return sp.get_auth_response()

@app.route('/sc')
def scUserLogin():
    #sc = soundcloud_auth()
    return render_template('oops.html')

@app.route('/am')
def appleUserLogin():
    #am = apple_auth()
    return render_template('oops.html')


# app.run()