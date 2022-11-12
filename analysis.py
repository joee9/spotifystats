import pandas as pd
import logging
from os.path import exists

from datetime import datetime, timedelta
from pytz import timezone
from dateutil.parser import parse
est = timezone('America/New_York')

from general import get_auth
from get_rp import get_rp
from structs import database, load_database
from secrets import home


def df_date_range(df, start, stop):

    # empty songlist-like dataframe
    items = pd.DataFrame(columns=['ID', 'Timestamp'])
    for row in df.iterrows():
        i, (id, timestamp) = row
        curr = parse(timestamp).astimezone(est)
        if start < curr < stop:
            items = items.append({'ID': id, 'Timestamp': timestamp}, ignore_index=True)

    return items

def daily_analysis(sp, start:datetime=None, stop:datetime=None, year_analysis=False, all=False):

    if stop is None:
        stop = datetime.now(tz=est)
    if start is None:
        start = datetime.now(tz=est).replace(microsecond=0, second=0, minute=0, hour=0)
    
    month_start = start.replace(day=1)

    yyyymm = f'{start:%Y-%m}'
    month_message = f'{start:%B}'

    if not exists(month_path := f'{home}/data/{yyyymm}-songlist.txt'):
        raise Exception('Songlist does not exist!')

    db = load_database(yyyymm)
    df = pd.read_csv(month_path)
    month_df = df_date_range(df, month_start, stop)
    today_df = df_date_range(df, start, stop)
    
    # current day
    db.add_df(sp, today_df)
    db.full_summary(sp, 'Today', all=all)
    db.clean()

    db.add_df(sp, month_df)
    db.full_summary(sp, month_message, all=all)

    if year_analysis:
        yyyy = yyyymm[0:4]
        full_year_analysis(sp, yyyy, db=db)
    else:
        db.dump()
    
def full_year_analysis(sp, yyyy, db=None):

    date_strs = [f'{yyyy}-{mm:02}' for mm in range(1,13)]

    valid_date_strs = []
    for ds in date_strs:
        if exists(f'{home}/data/{ds}-songlist.txt'):
            valid_date_strs.append(ds)
    
    all_db = database()
    dbs = []
    for yyyymm in valid_date_strs:
        db = load_database(yyyymm)
        df = pd.read_csv(f'{home}/data/{yyyymm}-songlist.txt')
        db.add_df(sp, df)
        db.full_summary(sp, db.get_month_str())

        all_db += db
        
        dbs.append(db)

    all_db.full_summary(sp, str(yyyy))

    for db in dbs:
        db.dump()

def main():
    sp = get_auth()
    get_rp(sp)

    daily_analysis(sp)
    full_year_analysis(sp, 2022)

if __name__ == '__main__':
    main()