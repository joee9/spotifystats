# Joe Nyhan, 24 October 2022
# General functions for spotifystats

# spotify libraries
import spotipy.util as util # for getting authorization
from spotipy.oauth2 import SpotifyOAuth
import spotipy              # for getting tracks, etc.

from secrets import username, client_id, client_secret, client_scope


def get_auth():
    redirect_uri = 'http://localhost:7777/callback'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=client_scope
    ))


    return sp