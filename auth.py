# Joe Nyhan, 07 March 2022
# Authorization functions for spotipy

import spotipy.util as util
import spotipy

from secrets import username, client_id, client_secret

def get_auth(scope='user-top-read'):
    redirect_uri = 'http://localhost:7777/callback'
    # scope = 'user-read-recently-played'
    # scope = 'user-top-read'

    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)