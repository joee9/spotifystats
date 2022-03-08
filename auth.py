# Joe Nyhan, 07 March 2022
# Returns correct spotify authorization token

import spotipy.util as util
import spotipy

from secrets import username, client_id, client_secret

def get_auth():
    redirect_uri = 'http://localhost:7777/callback'
    scope = 'user-top-read playlist-modify-public user-read-recently-played'

    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)