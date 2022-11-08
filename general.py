# Joe Nyhan, 24 October 2022
# General functions for spotifystats

# spotify libraries
import spotipy.util as util # for getting authorization
import spotipy              # for getting tracks, etc.

from secrets import username, client_id, client_secret, client_scope


def get_auth():
    redirect_uri = 'http://localhost:7777/callback'

    token = util.prompt_for_user_token(username=username, scope=client_scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)