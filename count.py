# Joe Nyhan, 7 January 2022
# Given a dataframe, will turn it into three ordered lists containing tracks, artists, and albums; also, updates database dictionaries as it goes

# spotify libraries
import spotipy.util as util
import spotipy

#system related
from os.path import exists
import json

# misc
import pandas as pd

# user specific details
from secrets import username, client_id, client_secret, client_scope, home_path

def get_auth():
    redirect_uri = 'http://localhost:7777/callback'
    # scope = 'user-read-recently-played'

    token = util.prompt_for_user_token(username=username, scope=client_scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)

def get_track_count(sp, id, tracks, db):
    if not id in tracks:
        if id in db:
            data = db[id]
            name = data['name']
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
                'artwork_url': album_artwork_url,
            }

        tracks[id] = {
            'name': name,
            'timestamps': [], # initalize to empty list
            'count': 0
        }

    return tracks[id]

def get_album_count(sp, id, albums, db):
    if not id in albums:
        if id in db:
            data = db[id]
            name = data['name']
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
            'timestamps': [], # initalize to empty list
            'count': 0
        }
    
    return albums[id]

def get_artist_count(sp, id, artists, db):
    if not id in artists:

        if id in db:
            data = db[id]
            name = data['name']
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

    track_info = get_track_count(sp, track_id, tracks, track_db)
    add_curr_song(track_info)

    album_info = get_album_count(sp, track_db[track_id]['album_id'], albums, album_db)
    add_curr_song(album_info)

    for artist_id in track_db[track_id]['artist_ids']:
        artist_info = get_artist_count(sp, artist_id, artists, artist_db)
        add_curr_song(artist_info)

def analyze_dataframe(sp, df, dbs):

    tracks = {}
    artists = {}
    albums = {}
    analyses = tracks, artists, albums

    for i in range(len(df)):
        analyze_track(sp, df.iloc[i,:], analyses, dbs)
    
    return tracks, artists, albums

def sort_items(dict):
    def sort_scheme(d): return -d['count'], d['name']

    total = 0
    result = []
    for id in dict.keys():
        d = dict[id]
        count = d['count']
        result.append({'id': id, 'name': d['name'], 'count': count})
        total += count
    
    result.sort(key=sort_scheme)

    return (result, total)

def get_counts(sp, df, dbs):
    track_cts, artist_cts, album_cts = analyze_dataframe(sp, df, dbs)
    track_cts, total = sort_items(track_cts)
    artist_cts, artist_total = sort_items(artist_cts)
    album_cts, album_total = sort_items(album_cts)
    return track_cts, artist_cts, album_cts, total


def print_top(list, num=10):
    list = list[0:num]
    for i, item in enumerate(list):
        name = item['name']
        count = item['count']
        print(f'{i+1:2d}. ({count}) {name:35s}')

def main():
    # test main
    sp = get_auth()

    yyyy_mm = '2022-01'
    path = f'{home_path}/data/{yyyy_mm}'
    db_path = f'{path}-database.txt'
    if exists(db_path):
        with open(db_path) as f:
            dbs = json.loads(f.read())
    else: 
        dbs = {},{},{}

    month_file = f'{path}-songlist.txt'
    df = pd.read_csv(month_file)

    result = get_counts(sp, df, dbs)

    with open(f'{path}-counts.txt','w') as f:
        f.write(json.dumps(result))
    
    with open(db_path, 'w') as f:
        f.write(json.dumps(dbs))

    track_cts, artist_cts, album_cts = result
    track_cts, track_total = track_cts
    artist_cts, artist_total = artist_cts
    album_cts, album_total = album_cts

    print_top(track_cts)
    print(track_total)
    print_top(artist_cts)
    print_top(album_cts)

if __name__ == '__main__':
    main()