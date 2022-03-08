# Joe Nyhan, 8 March 2022
# creates an ouath2 token for spotify api

import spotipy.util as util # for getting authorization
import spotipy              # for getting tracks, etc.

from secrets import client_id, client_secret, username

def get_auth():
    redirect_uri = 'http://localhost:7777/callback'
    # scope = 'user-read-recently-played'
    scope = 'user-top-read playlist-modify-public user-read-recently-played'

    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)