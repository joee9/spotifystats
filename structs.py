import logging
# logging.basicConfig(level=logging.INFO)
from os.path import exists
import json

from datetime import datetime, timedelta
from pytz import timezone
est = timezone('America/New_York')

from secrets import home


class music:
    """
    a general class for album, artist, and album; there are consistent operations performed on all three. The big difference between all three of the aforementioned objects is the data fields; however, each will have the same
    - hash format
    - timestamp setup
    - counts
    """

    def __init__(self, id, ts) -> None:
        self.id = id
        self.attributes = False

        if ts is None:
            self.timestamps = []
            self.count = 0
            return

        self.timestamps = [ts]
        self.count = 1
    
    def __hash__(self) -> int:
        return hash(self.id)

    def add_instance(self, ts):
        self.timestamps.append(ts)
        self.count += 1
    
    def __str__(self) -> str:
        return f'{self.count:3}, {self.name} ({self.id})'
    
    def set_attributes(self, sp, data=None):
        if not self.attributes:
            self.attributes = self.get_data(sp, data)
    
    def get_name(self):
        """
        precondition: name has already been set
        """
        return self.name
    
    def get_count(self):
        return self.count
    
    def reset(self):
        self.timestamps = []
        self.count = 0
    
class album(music):

    name = None
    url = None
    artist_ids = None
    artwork_url = None

    def get_data(self, sp, data=None) -> bool:

        if data is not None:
            if not data['attributes']:
                return False
            self.name = data['name']
            self.url = data['url']
            self.artist_ids = data['artist_ids']
            self.artwork_url = data['artwork_url']
            return True

        data = sp.album(self.id)

        self.name = data['name']
        self.url = data['external_urls']['spotify']

        self.artist_ids = [i['id'] for i in data['artists']]
        self.artwork_url = data['images'][1]['url']
        return True
    
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

    def get_data(self, sp, data=None) -> bool:

        if data is not None:
            if not data['attributes']:
                return False
            self.name = data['name']
            self.url = data['url']
            self.artwork_url = data['artwork_url']
            self.genres = data['genres']
            return True

        data = sp.artist(self.id)

        self.name = data['name']
        self.url = data['external_urls']['spotify']

        self.artwork_url = data['images'][1]['url']
        self.genres = data['genres']

        return True
    
    def get_genres(self):
        return ', '.join(self.genres).title()

class track(music):

    name = None
    url = None
    artist_ids = None
    album_id = None
    
    def get_data(self, sp, data=None) -> bool:

        if data is not None:
            if not data['attributes']:
                return False
            self.name = data['name']
            self.url = data['url']
            self.artist_ids = data['artist_ids']
            self.album_id = data['album_id']
            return True

        data = sp.track(self.id)

        self.name = data['name']
        self.url = data['external_urls']['spotify']

        self.artist_ids = [i['id'] for i in data['album']['artists']]
        self.album_id = data['album']['id']
        return True

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

    def __init__(self, df=None, sp=None, yyyymm=None) -> None:
        self.tracks = {}
        self.albums = {}
        self.artists = {}
        self.total = 0

        if df is not None:
            if sp is not None:
                self.from_df(sp, df)
            else:
                raise Exception('To load from df, an sp token must also be passed.')
        
        self.yyyymm = yyyymm
    
    def add_df(self, sp, df):
        for row in df.iterrows():
            i, (id, ts) = row
            if i % 10 == 0:
                logging.info(f'{i=}')
            self.add_track(sp, id, ts)
            self.total += 1
    
    def clean(self):

        def reset_dict(d):
            for v in d.values():
                v.reset()

        reset_dict(self.albums)
        reset_dict(self.artists)
        reset_dict(self.tracks)

        self.total = 0
    
    def dump(self):
        
        yyyymm = self.get_yyyymm()
        if yyyymm is None:
            raise Exception('Cannot dump unless yyyymm is specified!')

        with open(f'{home}/data/{self.get_yyyymm()}-database.json', 'w') as out:
            self.clean()
            json.dump(self.to_dict(), out)

    def to_dict(self):
        def serialize_music_dict(d):
            new_d = {}
            for id,m in d.items():
                new_d[id] = m.__dict__
            return new_d
        
        all = {}
        all['tracks'] = serialize_music_dict(self.tracks)
        all['albums'] = serialize_music_dict(self.albums)
        all['artists'] = serialize_music_dict(self.artists)
        all['yyyymm'] = self.yyyymm

        return all

    def from_dict(self, data):
        """
        assumes a json serialized dictionary containing all necessary data

        Note: only entries containing sp data are written to file, so we can assume that all those read in will contain necessary data; e.g. 'name' cannot be None
        """
        def deserialize_music_dict(d, mus: music):
            new_d = {}
            for id,m_dict in d.items():
                m = mus(id, None)
                m.set_attributes(None, data=m_dict)
                new_d[id] = m
            return new_d

        # print(data['tracks'])

        self.tracks = deserialize_music_dict(data['tracks'], track)
        self.albums = deserialize_music_dict(data['albums'], album)
        self.artists = deserialize_music_dict(data['artists'], artist)
        self.yyyymm = data['yyyymm']

    def add(self, other):
        """
        add two *distinct* dictionaries; assumes that elements in one are not in the other. This would affect the counts/timestamps, and items would be overcounted
        """

        def merge_dicts(a,b):
            # iterate over all items in b and add them to a if necessary
            for key,bv in b.items():

                # this item *is* in a
                if (av:=a.get(key)) is not None:

                    # we have two "music" objects of the same id; need to merge timestamps and counts, and ensure if one of the dbs has the attributes, we keep them

                    all_ts = av.timestamps + bv.timestamps
                    total_count = av.count + bv.count

                    # pull in attribues if necessary
                    if (not av.attributes) and bv.attributes:
                        av = bv

                    av.timestamps = all_ts
                    av.count = total_count

                # item is not in a
                else:
                    a[key] = bv

        merge_dicts(self.albums, other.albums)
        merge_dicts(self.artists, other.artists)
        merge_dicts(self.tracks, other.tracks)

        self.total += other.total
    
    def __iadd__(self, other):
        self.add(other)
        return self

    def __add_music(self, db, mus: music, id, ts):
        if (m:=db.get(id)) is None:
            db[id] = mus(id, ts)
        else:
            m.add_instance(ts)

        return db[id]

    def add_album(self, album_id, ts):
        return self.__add_music(self.albums, album, album_id, ts)
    
    def add_artist(self, artist_id, ts):
        return self.__add_music(self.artists, artist, artist_id, ts)
        
    def add_track(self, sp, track_id, ts):
        t = self.__add_music(self.tracks, track, track_id, ts)
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

    def set_artist_data(self, sp, artist_ids):
        """
        precondition: all artist_ids are already in the artist db
        """
        for id in artist_ids:
            self.artists[id].set_attributes(sp)

    def formatted_album_str(self, sp, album_id):
        """
        precondition: album_id is already in the album dict
        """
        self.set_album_data(sp, album_id)
        return self.albums[album_id].get_name()

    def formatted_artist_str(self, sp, artist_ids):
        """
        precondition: all artist ids given are already in the artists_db; should be the case if done in the correct order, i.e. all tracks read in and add ids added along the way
        """
        self.set_artist_data(sp, artist_ids)
        names = [self.artists[id].get_name() for id in artist_ids]
        return ', '.join(names)
    
    def __get_top_music(self, sp, music_dict, num=10):
        """
        return a sorted top list of a music type of length num; sorted by count, then name; num=-1 returns the whole list. If num > total number of songs, it returns the whole list
        """
        all_music = sorted(music_dict.values(), key=lambda m: -m.get_count())

        sort_ct_then_name = lambda t: (-t.get_count(), t.get_name())

        if num > len(all_music) or num == -1: 
            for m in all_music:
                m.set_attributes(sp)
            return sorted(all_music, key=sort_ct_then_name)

        n = num
        curr = all_music[n-1]
        last_ct = curr.get_count()
        while curr.get_count() >= last_ct and (n < len(all_music)):
            n += 1
            curr = all_music[n-1]
        
        top_music = all_music[0:n]
        for m in top_music:
            m.set_attributes(sp)
        
        # as all attributes are set, we can sort by count, then name 
        return sorted(top_music, key=sort_ct_then_name)[0:num]

    def get_top_tracks(self, sp, num=10):
        return self.__get_top_music(sp, self.tracks, num=num)
    
    def get_top_albums(self, sp, num=10):
        return self.__get_top_music(sp, self.albums, num=num)

    def get_top_artists(self, sp, num=10):
        return self.__get_top_music(sp, self.artists, num=num)
    
    def __print_out_str(self, i, m: music, s):
        if (ct := m.count) == 0:
            return
        count_str = f'({ct})'
        print(f'{i:2}. {count_str:>5} {s}')

    def print_top_tracks(self, sp, num=10, message=''):

        top_tracks = self.get_top_tracks(sp, num=num)

        if message != '':
            message += "'s "
            message = message.upper()

        print(f'{message}TOP TRACKS')
        print(f'Total plays: {self.total}')
        for i,t in enumerate(top_tracks, start=1):
            artist_str = self.formatted_artist_str(sp, t.get_artist_ids())
            album_str = self.formatted_album_str(sp, t.get_album_id())
            out_str = f'{t.get_name()}, by {artist_str}, in {album_str}'

            self.__print_out_str(i, t, out_str)

        print('')
    
    def print_top_artists(self, sp, num=5):

        top_artists = self.get_top_artists(sp, num=num)

        print('TOP ARTISTS')
        for i,a in enumerate(top_artists, start=1):
            self.__print_out_str(i, a, f'{a.get_name()}: {a.get_genres()}')

        print('')

    def print_top_albums(self, sp, num=5):

        top_albums = self.get_top_albums(sp, num=num)

        print('TOP ALBUMS')
        for i,a in enumerate(top_albums, start=1):
            artist_str = self.formatted_artist_str(sp, a.get_artist_ids())
            self.__print_out_str(i, a, f'{a.get_name()}, by {artist_str}')
        
        print('')

    def print_top(self, sp, message='', all=False):
        if all:
            self.print_top_tracks(sp, message=message, num=-1)
            self.print_top_artists(sp, num=-1)
            self.print_top_albums(sp, num=-1)
            return

        self.print_top_tracks(sp, message=message)
        self.print_top_artists(sp)
        self.print_top_albums(sp)

    def full_summary(self, sp, message='', all=False):
        self.print_top(sp, message, all=all)

    def verify_year(self, yyyymm: str) -> bool:
        return (self.yyyymm == yyyymm)

    def get_yyyymm(self):
        return self.yyyymm

    def get_month_str(self):
        yyyy, mm = self.yyyymm.split('-')
        yyyy, mm = int(yyyy), int(mm)
        dt = datetime(year=yyyy, month=mm, day=1)
        return f'{dt:%B}'

def load_database(yyyymm: str) -> database:
    """
    initializes a database with songs from month yyyymm and cached data from optional database
    """
    db = database(yyyymm=yyyymm)
    if exists(db_path:=f'{home}/data/{yyyymm}-database.json'):
        with open(db_path, 'r') as infile:
            data = json.load(infile)
        
        db.from_dict(data)

    if db.verify_year(yyyymm):
        return db
    raise Exception('db is (somehow) from the wrong year!')


def main():
    print('Testing has now been moved to "analysis.py".')
    pass

if __name__ == '__main__':
    main()