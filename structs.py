import pandas as pd
import logging

from general import get_auth

class music:
    """
    a general class for album, artist, and album; there are consistent operations performed on all three. The big difference between all three of the aforementioned objects is the data fields; however, each will have the same
    - hash format
    - timestamp setup
    - counts
    """

    def __init__(self, id, ts) -> None:
        self.id = id
        self.timestamps = [ts]
        self.count = 1
        self.attributes = False
    
    def __hash__(self) -> int:
        return hash(self.id)

    def add_instance(self, ts):
        self.timestamps.append(ts)
        self.count += 1
    
    def __str__(self) -> str:
        return f'{self.count:3}, {self.name} ({self.id})'
    
    def set_attributes(self, sp):
        if not self.attributes:
            self.get_data(sp)
            self.attributes = True
    
    def get_name(self):
        """
        precondition: name has already been set
        """
        return self.name
        
class album(music):

    name = None
    url = None
    artist_ids = None
    artwork_url = None

    def get_data(self, sp):

        data = sp.album(self.id)

        self.name = data['name']
        self.url = data['external_urls']['spotify']

        self.artist_ids = [i['id'] for i in data['artists']]
        self.artwork_url = data['images'][1]['url']
    
    def get_artist_ids(self):
        """
        precondition: requires attributes to already be set
        """
        return self.artist_ids

class artist(music):

    name = None
    url = None
    artwork_url = None
    genres = None

    def get_data(self, sp):

        data = sp.artist(self.id)

        self.name = data['name']
        self.url = data['external_urls']['spotify']

        self.artwork_url = data['images'][1]['url']
        self.genres = data['genres']

class track(music):

    name = None
    url = None
    artist_ids = None
    album_id = None
    
    def get_data(self, sp):
        data = sp.track(self.id)

        self.name = data['name']
        self.url = data['external_urls']['spotify']

        self.artist_ids = [i['id'] for i in data['album']['artists']]
        self.album_id = data['album']['id']

    def get_artist_ids(self):
        """
        precondition: requires attributes to already be set
        """
        return self.artist_ids
    
    def get_album_id(self):
        """
        precondition: requires attributes to already be set
        """
        return self.album_id
    
class database:

    def __init__(self, df=None, sp=None) -> None:
        self.tracks = {}
        self.albums = {}
        self.artists = {}
        self.total = 0

        if df is not None:
            if sp is not None:
                self.add_from_db(sp, df)
            else:
                raise Exception('To load from df, an sp token must also be passed.')
    
    def add_from_db(self, sp, df):
        for row in df.iterrows():
            i, (id, ts) = row
            logging.info(f'{i=}')
            self.add_track(sp, id, ts)
    
    def add_music(self, db, mus: music, id, ts):
        if (m:=db.get(id)) is None:
            db[id] = mus(id, ts)
        else:
            m.add_instance(ts)

        return db[id]

    def add_album(self, album_id, ts):
        return self.add_music(self.albums, album, album_id, ts)
    
    def add_artist(self, artist_id, ts):
        return self.add_music(self.artists, artist, artist_id, ts)
        
    def add_track(self, sp, track_id, ts):
        t = self.add_music(self.tracks, track, track_id, ts)
        t.set_attributes(sp)

        artist_ids = t.get_artist_ids()
        for artist_id in artist_ids:
            self.add_artist(artist_id, ts)

        album_id = t.get_album_id()
        self.add_album(album_id, ts)
    
    def set_album_data(self, sp, album_id):
        """
        precondition: album_id is already in the album dict
        """
        album = self.albums[album_id]
        album.set_attributes(sp)

    def formatted_album_str(self, sp, album_id):
        """
        precondition: album_id is already in the album dict
        """
        self.set_album_data(sp, album_id)
        return self.albums[album_id].get_name()

    def set_artist_data(self, sp, artist_ids):
        """
        precondition: all artist_ids are already in the artist db
        """
        for id in artist_ids:
            self.artists[id].set_attributes(sp)

    def formatted_artist_str(self, sp, artist_ids):
        """
        precondition: all artist ids given are already in the artists_db; should be the case if done in the correct order, i.e. all tracks read in and add ids added along the way
        """
        self.set_artist_data(sp, artist_ids)
        s = ''
        for i,id in enumerate(artist_ids):
            artist = self.artists[id]
            s += f'{artist.get_name()}, '
            if i == len(artist_ids)-1:
                s = s[:-2]
        return s
    
    def get_top_music(self, music_dict, num=10):
        all_music = sorted(music_dict.values(), key=lambda m: -m.count)

        if num > len(all_music):
            logging.warning(f'"num" parameter with value {num} is longer than whole list.')
            num = len(all_music)
        if num == -1:
            num = len(all_music)

        return all_music[0:num]
    
    def get_top_tracks(self, num=10):
        return self.get_top_music(self.tracks, num=num)
    
    def get_top_albums(self, num=10):
        return self.get_top_music(self.albums, num=num)

    def get_top_artists(self, num=10):
        return self.get_top_music(self.artists, num=num)
    
    # these three print functions could likely be combined and the print string changed for each type of "music", but this was easy for the time being. Its not perfectly object oriented, but c'est la vie...

    def print_top_tracks(self, sp, num=10):

        top_tracks = self.get_top_tracks(num=num)

        print('TOP TRACKS')
        for i,t in enumerate(top_tracks, start=1):
            artist_str = self.formatted_artist_str(sp, t.get_artist_ids())
            album_str = self.formatted_album_str(sp, t.get_album_id())
            count_str = f'({t.count})'
        
            print(f'{i:2}: {count_str:>5} {t.get_name()}, by {artist_str}, in {album_str}')

        print('')
    
    def print_top_artists(self, sp, num=10):

        top_artists = self.get_top_artists(num=num)

        print('TOP ARTISTS')
        for i,a in enumerate(top_artists, start=1):
            a.set_attributes(sp)
            count_str = f'({a.count})'
            print(f'{i:2}: {count_str:>5} {a.get_name()}')

        print('')

    def print_top_albums(self, sp, num=10):

        top_albums = self.get_top_albums(num=num)

        print('TOP ALBUMS')
        for i,a in enumerate(top_albums, start=1):
            a.set_attributes(sp)
            artist_str = self.formatted_artist_str(sp, a.get_artist_ids())
            count_str = f'({a.count})'
            print(f'{i:2}: {count_str:>5} {a.get_name()}, by {artist_str}')
        
        print('')

        
def main():
    sp = get_auth()

    df = pd.read_csv(f'./data/2022-11-songlist.txt')
    db = database(df=df, sp=sp)
    
    db.print_top_tracks(sp, num=-1)
    db.print_top_albums(sp, num=-1)
    db.print_top_artists(sp, num=-1)


if __name__ == '__main__':
    main()