# Joe Nyhan, 6 January 2022
# Given a dataframe, will turn it into three dictionaries, containing all important information about a month

# spotify libraries
import spotipy.util as util
import spotipy

#system related
from os.path import exists
import json

# misc
import pandas as pd

# user specific details
from secrets import username, client_id, client_secret, home_path

def get_auth():
    redirect_uri = 'http://localhost:7777/callback'
    # scope = 'user-read-recently-played'
    scope = 'user-top-read'

    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)

def get_track_entry(sp, id, tracks, db):
    if not id in tracks:
        if id in db:
            data = db[id]
            name = data['name']
            sp_url = data['url']
            artist_names = data['artist_names']
            artist_ids = data['artist_ids']
            album_name = data['album_name']
            album_id = data['album_id']
            album_artwork_url = data['album_artwork_url']
        else: 
            data = sp.track(id)
            name = data['name']
            sp_url = data['external_urls']['spotify']

            artist_names = []
            artist_ids = []
            for entry in data['album']['artists']:
                artist_names.append(entry['name'])
                artist_ids.append(entry['id'])
            
            album_name = data['album']['name']
            album_id = data['album']['id']
            album_artwork_url = data['album']['images'][1]['url']

            db[id] = {
                'name': name,
                'url': sp_url,
                'artist_names': artist_names,
                'artist_ids': artist_ids,
                'album_name': album_name,
                'album_id': album_id,
                'album_artwork_url': album_artwork_url,
            }

        tracks[id] = {
            'name': name,
            'url': sp_url,
            'artist_names': artist_names,
            'artist_ids': artist_ids,
            'album_name': album_name,
            'album_id': album_id,
            'album_artwork_url': album_artwork_url,
            'timestamps': [], # initalize to empty list
            'count': 0
        }

    return tracks[id]

def get_album_entry(sp, id, albums, db):
    if not id in albums:
        if id in db:
            data = db[id]
            name = data['name']
            sp_url = data['url']
            artist_names = data['artist_names']
            artist_ids = data['artist_ids']
            artwork_url = data['artwork_url']
        else:


            data = sp.album(id)
            name = data['name']
            sp_url = data['external_urls']['spotify']

            artist_names = []
            artist_ids = []
            for entry in data['artists']:
                artist_names.append(entry['name'])
                artist_ids.append(entry['id'])

            artwork_url = data['images'][1]['url']

            db[id] = {
                'name': name,
                'url': sp_url,
                'artist_names': artist_names,
                'artist_ids': artist_ids,
                'artwork_url': artwork_url,
            }

        albums[id] = {
            'name': name,
            'url': sp_url,
            'artist_names': artist_names,
            'artist_ids': artist_ids,
            'artwork_url': artwork_url,
            'timestamps': [], # initalize to empty list
            'count': 0
        }
    
    return albums[id]

def get_artist_entry(sp, id, artists, db):
    if not id in artists:

        if id in db:
            data = db[id]
            name = data['name']
            sp_url = data['url']
            artwork_url = data['artwork_url']
            genres = data['genres']
        else:
            data = sp.artist(id)

            name = data['name']
            sp_url = data['external_urls']['spotify']
            artwork_url = data['images'][1]['url']
            genres = data['genres']

            db[id] = {
                'name': name,
                'url': sp_url,
                'artwork_url': artwork_url,
                'genres': genres,
            }

        artists[id] = {
            'name': name,
            'url': sp_url,
            'artwork_url': artwork_url,
            'genres': genres,
            'timestamps': [], # initalize to empty list
            'count': 0
        }
    
    return artists[id]


def analyze_track(sp, row, analyses, dbs):
    track_id, timestamp = row
    track_db, artist_db, album_db = dbs
    tracks, artists, albums = analyses

    def add_curr_song(info):
        info['timestamps'].append(timestamp)
        info['count'] += 1

    track_info = get_track_entry(sp, track_id, tracks, track_db)
    add_curr_song(track_info)

    album_info = get_album_entry(sp, track_info['album_id'], albums, album_db)
    add_curr_song(album_info)

    for artist_id in track_info['artist_ids']:
        artist_info = get_artist_entry(sp, artist_id, artists, artist_db)
        add_curr_song(artist_info)

def parse_dataframe(sp, df, yyyy_mm):

    path = f'{home_path}/data/{yyyy_mm}'
    db_path = f'{path}-database.txt'
    if exists(db_path):
        with open(db_path) as f:
            dbs = json.loads(f.read())
    else: 
        dbs = {},{},{}

    tracks = {}
    artists = {}
    albums = {}
    analyses = tracks, artists, albums

    for i in range(len(df)):
        analyze_track(sp, df.iloc[i,:], analyses, dbs)
    
    with open(db_path, 'w') as f:
        f.write(json.dumps(dbs))
    
    return tracks, artists, albums

def sort_items(dict):
    def sort_scheme(d): return -d['count'], d['name']

    result = []
    for id in dict.keys():
        d = dict[id]
        result.append({'id': id, 'name': d['name'], 'count': d['count']})
    
    result.sort(key=sort_scheme)

    return result
    

def main():
    sp = get_auth()

    month_file = f'{home_path}/data/2021-12-songlist.txt'
    df = pd.read_csv(month_file)

    result = parse_dataframe(sp, df, '2021-12')
    with open(f'{home_path}/data/2021-12-parsed.txt','w') as f:
        f.write(json.dumps(result))
    

if __name__ == '__main__':
    main()