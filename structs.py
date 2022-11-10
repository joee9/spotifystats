import pandas as pd
import logging
from os.path import exists
import pickle
# logging.basicConfig(level=logging.INFO)

from datetime import datetime, timedelta
from pytz import timezone
from dateutil.parser import parse
est = timezone('America/New_York')

from general import get_auth
from get_rp import get_rp


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
                self.from_df(sp, df)
            else:
                raise Exception('To load from df, an sp token must also be passed.')
    
    def add_df(self, sp, df):
        for row in df.iterrows():
            i, (id, ts) = row
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

                    av.timesteps = all_ts
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
        s = ''
        for i,id in enumerate(artist_ids):
            artist = self.artists[id]
            s += f'{artist.get_name()}, '
            if i == len(artist_ids)-1:
                s = s[:-2]
        return s
    
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
    
    # these three print functions could likely be combined and the print string changed for each type of "music", but this was easy for the time being. Its not perfectly object oriented, but c'est la vie...

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
            count_str = f'({t.count})'
        
            print(f'{i:2}. {count_str:>5} {t.get_name()}, by {artist_str}, in {album_str}')

        print('')
    
    def print_top_artists(self, sp, num=5):

        top_artists = self.get_top_artists(sp, num=num)

        print('TOP ARTISTS')
        for i,a in enumerate(top_artists, start=1):
            count_str = f'({a.count})'
            print(f'{i:2}. {count_str:>5} {a.get_name()}')

        print('')

    def print_top_albums(self, sp, num=5):

        top_albums = self.get_top_albums(sp, num=num)

        print('TOP ALBUMS')
        for i,a in enumerate(top_albums, start=1):
            artist_str = self.formatted_artist_str(sp, a.get_artist_ids())
            count_str = f'({a.count})'
            print(f'{i:2}. {count_str:>5} {a.get_name()}, by {artist_str}')
        
        print('')

    def print_top(self, sp, message=''):
        self.print_top_tracks(sp, message=message)
        self.print_top_artists(sp)
        self.print_top_albums(sp)

    def full_summary(self, sp, message=''):
        self.print_top(sp, message)

def load_database(yyyymm: str) -> database:
    """
    initializes a database with songs from month yyyymm and cached data from optional database
    """
    if exists(db_path:=f'./data/{yyyymm}-database.pickle'):
        with open(db_path, 'rb') as infile:
            db = pickle.load(infile)
    else:
        db = database()

    return db

def dump_database(yyyymm: str, db: database):
    with open(f'./data/{yyyymm}-database.pickle', 'wb') as out:
        db.clean()
        pickle.dump(db, out)

def df_date_range(df, start, stop):

    # empty songlist-like dataframe
    items = pd.DataFrame(columns=['ID', 'Timestamp'])
    for row in df.iterrows():
        i, (id, timestamp) = row
        curr = parse(timestamp).astimezone(est)
        if start < curr < stop:
            items = items.append({'ID': id, 'Timestamp': timestamp}, ignore_index=True)

    return items

def daily_analysis(sp, start:datetime=None, stop:datetime=None, year_analysis=False):

    if stop is None:
        stop = datetime.now(tz=est)
    if start is None:
        start = datetime.now(tz=est).replace(microsecond=0, second=0, minute=0, hour=0)

    yyyymm = f'{start:%Y-%m}'
    month_message = f'{start:%B}'

    if not exists(month_path := f'./data/{yyyymm}-songlist.txt'):
        raise Exception('Songlist does not exist!')

    db = load_database(yyyymm)
    month_df = pd.read_csv(month_path)
    today_df = df_date_range(month_df, start, stop)
    
    # current day
    db.add_df(sp, today_df)
    db.full_summary(sp, 'Today')
    db.clean()

    db.add_df(sp, month_df)
    db.full_summary(sp, month_message)

    if year_analysis:
        yyyy = yyyymm[0:4]
        year_analysis(sp, yyyy, db)
    else:
        dump_database(yyyymm, db)

def year_analysis(sp, yyyy, db):
    pass
        
def main():
    sp = get_auth()
    get_rp(sp)

    # mms = ['01', '02', '03', '04', '05']#, '11']
    # # mms = ['11']

    # all_db = database()

    # dbs = []

    # # TODO: need to make dump, init more oo

    # for mm in mms:
    #     yyyymm = f'2022-{mm}'
    #     print(yyyymm)

    #     db = load_database(sp, yyyymm)
    #     print(db.total)

    #     all_db += db

    #     dbs.append((yyyymm, db))
    
    # all_db.print_top(sp)

    # for yyyymm, db in dbs:
    #     dump_database(yyyymm, db)

    start = datetime.now(tz=est).replace(microsecond=0, second=0, minute=0, hour=0, day=16, month=5)

    stop = start + timedelta(days=1, minutes=-1)

    daily_analysis(sp)
    daily_analysis(sp, start=start, stop=stop)

if __name__ == '__main__':
    main()