# Joe Nyhan, 26 December 2021; updated 7 January 2021
# Produces a LaTeX generated .pdf and .txt file with top songs, artists, and albums of the day and month

full_summary = True
# full_summary = False

#%%
# spotify libraries
import spotipy.util as util
import spotipy

# time related
from datetime import datetime, timedelta
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser

#system related
import os
import sys
import json

# misc
import pandas as pd
import numpy as np
from urllib.request import urlretrieve
from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt

# user specific details
from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path, sender
from count import get_counts

def get_auth():
    redirect_uri = 'http://localhost:7777/callback'
    # scope = 'user-read-recently-played'
    scope = "user-top-read"

    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)

def start_of_day_est(dto):
    """
    given a datetime object, returns a datetime object corresponding to the very beginning of the inputted day in EST
    """
    return dto.astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)

def format_artist_names(artists):
    """
    track_info: insert spotify track object; returns formatted string of the artist names
    """
    # artists = track_info["album"]["artists"]
    num_artists = len(artists)
    artist_names = ""

    for i in range(num_artists):
        if i == num_artists-1:
            artist_names += artists[i]
        else: artist_names += artists[i] + ", "

    return artist_names

def make_image_circular(input_path, output_path):
    img = Image.open(input_path)
    height,width = img.size
    lum_img = Image.new('L', [height,width] , 0)

    draw = ImageDraw.Draw(lum_img)
    draw.pieslice([(0,0), (height,width)], 0, 360, fill = 255, outline = "white")
    img_arr = np.array(img)
    lum_img_arr = np.array(lum_img)
    final_img_arr = np.dstack((img_arr,lum_img_arr))

    img = Image.fromarray(final_img_arr)
    img.save(output_path)

def make_df_range(df, start, end):
    """
    Given a dataframe, a starting date and an ending date (both datetime objects), return a data frame of the value counts for song ids
    """
    songs = pd.DataFrame(columns=["ID","Timestamp"])
    for i in range(len(df)):
        timestamp = df.iloc[i,1]
        parsed = parser.parse(timestamp).astimezone(est)
        if  parsed > start and parsed < end:
            songs = songs.append(df.iloc[i,:])
    
    return songs

def get_album_artwork(album_id, artwork_url):
    """
    gets image by AlbumID, and stores in local database if not already present
    """
    im_path = f"{home_path}/analysis/images/{album_id}.jpg"
    if not os.path.exists(im_path):
        urlretrieve(artwork_url, im_path)
    return im_path

def get_artist_artwork(artist_id, artwork_url):
    """
    gets image by AlbumID, and stores in local database if not already present
    """
    im_path = f"{home_path}/analysis/artist_images/{artist_id}.jpg"
    if not os.path.exists(im_path):
        temp_path = im_path[0:len(im_path)-4] + "temp.jpg"
        urlretrieve(artwork_url, temp_path)

        # crop image to a square
        im = Image.open(temp_path)
        w, h = im.size
        c = min(w,h)
        cropped_im = im.crop(((w-c) // 2, (h-c) // 2, (w+c) // 2, (h+c) // 2))
        cropped_im.save(im_path)

        os.system(f"rm {temp_path}")

    return im_path

def make_top_songs(counts, file, message, db):
    """
    prints out the top songs for a given pd.series containing counts
    """
    song_cts, artists, albums, total = counts
    if len(song_cts) > 10: song_cts = song_cts[0:10]

    file.write(message + "\n")

    for song in song_cts:
        id = song['id']
        track_info = db[id]
        name = song['name']
        count = song['count']

        artist_names = format_artist_names(track_info['artist_names'])
    
        file.write(f"{count:3d}  {name}, by {artist_names}\n")
    
    file.write(f"Total songs played: {total}\n")

def replace_latex_special_characters(s):

    if "&" in s: s = s.replace("&", "\&")
    if "$" in s: s = s.replace("$", "\$")
    if "#" in s: s = s.replace("#", "\#")
    if "%" in s: s = s.replace("%", "\%")

    return s

def make_formatted_top_songs(songs, file, message, total, track_db, percent=False):
    """
    make a formatted LaTeX minipage containing album artwork, artist names, song titles, and counts
    """
    # # add comma if necessary (assumes 4 digit numbers max)
    tot = total
    total = str(total)
    if len(total) == 4:
        total = total[0] + "," + total[1:]
    elif len(total) == 5:
        total = total[:2] + "," + total[2:]

    ltf = False

    if len(songs) < 5:
        ltf = True

    if len(songs) > 10:
        songs = songs[0:10]   

    file.write("\\noindent\\LARGE{" + message + "'s Top Songs}\\hfill \\large{" + f"Total songs played: {total}" + "}\\\\[10pt]\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")

    def count_percent(count):
        ct_pct = count / tot * 100
        return f'({count}: {ct_pct:.1f}%) '

    def write(song):
        
        id = song['id']
        track_info = track_db[id]
        pic_path = get_album_artwork(track_info['album_id'], track_info['artwork_url'])
        name = track_info['name']
        if percent: count = count_percent(song['count'])
        else:       count = f"({song['count']}) "
        artist_names = count + format_artist_names(track_info['artist_names'])
        sp_url = track_info['url']

        # replace latex special characters
        name = replace_latex_special_characters(name)
        artist_names = replace_latex_special_characters(artist_names)
        # if "&" in name: name = name.replace("&", "\&")
        # if "$" in name: name = name.replace("$", "\$")
        # if "#" in name: name = name.replace("#", "\#")
        # if "%" in name: name = name.replace("%", "\%")
        # if "&" in artist_names: artist_names = artist_names.replace("&", "\&")
        # if "$" in artist_names: artist_names = artist_names.replace("$", "\$")
        # if "#" in artist_names: artist_names = artist_names.replace("#", "\#")
        # if "%" in artist_names: artist_names = artist_names.replace("%", "\%")

        file.write("\\begin{minipage}{.2\\textwidth}\n")
        file.write("\\href{" + sp_url + "}{\\includegraphics[width = \\textwidth]{" + pic_path + "}}\n")
        file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
        file.write("\\begin{minipage}{.75\\textwidth}\n")
        file.write("\\small \\textbf{\\truncate{\\textwidth}{" + name + "} }\\\\[2pt]\n")
        file.write("\\footnotesize \\truncate{\\textwidth}{" + artist_names + "}\n")
        file.write("\\end{minipage}\\\\[5pt]\n")
        file.write("\n")

    upp = 5
    if len(songs) < upp: upp = len(songs)
    for i in range(upp):
        write(songs[i])

    file.write("\\end{minipage}\\hfill%\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")
    
    if not ltf:
        upp = 10 
        if len(songs) < upp: upp = len(songs)
        for i in range(5,upp):
            write(songs[i])
    
    file.write("\\end{minipage}\n")
    file.write("\\vspace{15pt}\n\n")

def make_formatted_top_artists_albums(file, artists, albums, artist_db, album_db, total, percent=False):
    """
    make a formatted LaTeX minipage containing album artwork, artist names, song titles, and counts
    """
    # # add comma if necessary (assumes 4 digit numbers max)


    if len(artists) > 5:
        artists = artists[0:5]   
    if len(albums) > 5:
        albums = albums[0:5]   

    def count_percent(count):
        ct_pct = count / total * 100
        return f'({count}: {ct_pct:.1f}%) '

    def write_artist(artist):
        
        id = artist['id']
        artist_info = artist_db[id]
        pic_path = get_artist_artwork(id, artist_info['artwork_url'])
        name = artist_info['name']
        if percent: count = count_percent(artist['count'])
        else:       count = f"({artist['count']}) "
        artist_names = count + format_artist_names(artist_info['genres']).title()
        sp_url = artist_info['url']

        # replace latex special characters
        name = replace_latex_special_characters(name)
        artist_names = replace_latex_special_characters(artist_names)

        file.write("\\begin{minipage}{.2\\textwidth}\n")
        file.write("\\href{" + sp_url + "}{\\includegraphics[width = \\textwidth]{" + pic_path + "}}\n")
        file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
        file.write("\\begin{minipage}{.75\\textwidth}\n")
        file.write("\\small \\textbf{\\truncate{\\textwidth}{" + name + "} }\\\\[2pt]\n")
        file.write("\\footnotesize \\truncate{\\textwidth}{"+ artist_names + "}\n")
        file.write("\\end{minipage}\\\\[2pt]\n")
        file.write("\n")

    def write_album(album):
        
        id = album['id']
        album_info = album_db[id]
        pic_path = get_album_artwork(id, album_info['artwork_url'])
        name = album_info['name']
        if percent: count = count_percent(album['count'])
        else:       count = f"({album['count']}) "
        artist_names = count + format_artist_names(album_info['artist_names'])
        sp_url = album_info['url']

        # replace latex special characters
        name = replace_latex_special_characters(name)
        artist_names = replace_latex_special_characters(artist_names)

        file.write("\\begin{minipage}{.2\\textwidth}\n")
        file.write("\\href{" + sp_url + "}{\\includegraphics[width = \\textwidth]{" + pic_path + "}}\n")
        file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
        file.write("\\begin{minipage}{.75\\textwidth}\n")
        file.write("\\small \\textbf{\\truncate{\\textwidth}{" + name + "} }\\\\[2pt]\n")
        file.write("\\footnotesize \\truncate{\\textwidth}{" + artist_names + "}\n")
        file.write("\\end{minipage}\\\\[2pt]\n")
        file.write("\n")

    file.write("\\noindent\\begin{minipage}{.47\\textwidth}\n")
    file.write("\\noindent\\LARGE{Top Artists}\\\\[10pt]\n")

    for artist in artists:
        write_artist(artist)

    file.write("\\end{minipage}\\hfill%\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")
    file.write("\\noindent\\LARGE{Top Albums}\\\\[10pt]\n")
    
    for album in albums:
        write_album(album)
    
    file.write("\\end{minipage}\n")
    file.write("\\vspace{15pt}\n\n")

def make_user_stamp(file, stamp_info):
    display_name, user_url, pic_path, tag = stamp_info
    file.write("\\vfill\\raggedleft\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")
    file.write("\\raggedleft")
    file.write("\\begin{minipage}{.75\\textwidth}\n")
    file.write("\\raggedleft\\large \\href{"+ user_url + "}{\\textbf{" + display_name +  "}}\\\\[2pt]\n")
    file.write(f"\\normalsize {tag}")
    file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
    file.write("\\begin{minipage}{.2\\textwidth}\n")
    file.write("\\includegraphics[width = \\textwidth]{" + pic_path + "}\n")
    file.write("\\end{minipage}\\end{minipage}\n")
    file.write("\\newpage\n")

def make_fullpage_summary(file, counts, dbs, stamp_info, message, pct=False):
    songs, artists, albums, total = counts
    track_db, artist_db, album_db = dbs
    make_formatted_top_songs(songs, file, message, total, track_db)
    make_formatted_top_artists_albums(file, artists, albums, artist_db, album_db, total, percent=pct)
    make_user_stamp(file, stamp_info)

def additional_analysis(file, dbs, cts, usr_info, month, day):

    def make_plot(info, name):
        parsed_ts = [parser.parse(t).astimezone(est) for t in info['timestamps']]
        # print(parsed_ts)

        # num_bins = (parsed_ts[-1] - parsed_ts[0]).days + 1
        # print(num_bins)
        # print(num_days)
        # print(day,month)
        bins = []
        for d in range((day-month).days+1):
            bins.append(month+timedelta(days=d))
        
        n, a_bins, patches = plt.hist(parsed_ts, bins)
        # n, bin_edges = np.histogram(parsed_ts, bins)
        # plt.bar(bins, n, align='center')

        locs, labels = plt.xticks()
        new_labels = []
        first_date = month

        delta = locs[1]-locs[0]
        for i, loc in enumerate(locs):
            l = timedelta(days = delta*i) + first_date
            lf = f'{l:%b %d}'
            new_labels.append(lf)

        plt.xticks(locs, new_labels)
        plt.savefig(f'{home_path}/analysis/plots/{name}.pdf')
        plt.close()

        return n
    
    # def write_info(info, dbs, type):

    #     file.write("\\begin{minipage}{.2\\textwidth}\n")
    #     file.write("\\href{" + sp_url + "}{\\includegraphics[width = \\textwidth]{" + pic_path + "}}\n")
    #     file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
    #     file.write("\\begin{minipage}{.75\\textwidth}\n")
    #     file.write("\\small \\textbf{\\truncate{\\textwidth}{" + name + "} }\\\\[2pt]\n")
    #     file.write("\\footnotesize \\truncate{\\textwidth}{" + artist_names + "}\n")
    #     file.write("\\end{minipage}\\\\[2pt]\n")
    #     file.write("\n")

    def write_stats(n):
        most_freq_day = month+timedelta(days=np.argmax(n).item())
        most_freq_ct = int(max(n))
        
        file.write(f"\\small \\textbf{{Total plays}}: {int(sum(n))}\\\\")
        file.write(f"\\small \\textbf{{Most played day}}: {most_freq_day:%B %d}, {most_freq_ct} plays\\\\")
        file.write(f"\\textbf{{Average Daily Plays}}: {np.average(n):.2f}")


    def write(plt_name, info_func, info_ct, info_db):
        n = make_plot(info_ct, plt_name)
        file.write("\\noindent\\begin{minipage}{.47\\textwidth}\n")
        info_func(info_ct, info_db)
        write_stats(n)

        file.write("\\end{minipage}\\hfill%\n")
        file.write("\\begin{minipage}{.47\\textwidth}\n")
        file.write("\\begin{flushright}\\includegraphics[width = \\textwidth]{" + f'{home_path}/analysis/plots/{plt_name}.pdf' + "}\\end{flushright}\n")
        file.write("\\end{minipage}\n")
        file.write("")

    def write_track(track_ct, track_db):

        file.write("\\noindent\\LARGE{Top Track!}\\\\[10pt]\n")
        track_info = track_db[track_ct['id']]

        pic_path = get_album_artwork(track_info['album_id'], track_info['artwork_url'])
        name = track_info['name']
        artist_names = format_artist_names(track_info['artist_names'])
        sp_url = track_info['url']
        name = replace_latex_special_characters(name)
        artist_names = replace_latex_special_characters(artist_names)
        
        file.write("\\begin{minipage}{.2\\textwidth}\n")
        file.write("\\href{" + sp_url + "}{\\includegraphics[width = \\textwidth]{" + pic_path + "}}\n")
        file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
        file.write("\\begin{minipage}{.75\\textwidth}\n")
        file.write("\\small \\textbf{\\truncate{\\textwidth}{" + name + "} }\\\\[2pt]\n")
        file.write("\\footnotesize \\truncate{\\textwidth}{" + artist_names + "}\n")
        file.write("\\end{minipage}\\\\[2pt]\n")
        file.write("\n")
    
    def write_album(album_ct, album_db):

        file.write("\\noindent\\LARGE{Top Album!}\\\\[10pt]\n")
        album_info = album_db[album_ct['id']]

        pic_path = get_album_artwork(album_ct['id'], album_info['artwork_url'])
        name = album_info['name']
        artist_names = format_artist_names(album_info['artist_names'])
        sp_url = album_info['url']
        name = replace_latex_special_characters(name)
        artist_names = replace_latex_special_characters(artist_names)
        
        file.write("\\begin{minipage}{.2\\textwidth}\n")
        file.write("\\href{" + sp_url + "}{\\includegraphics[width = \\textwidth]{" + pic_path + "}}\n")
        file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
        file.write("\\begin{minipage}{.75\\textwidth}\n")
        file.write("\\small \\textbf{\\truncate{\\textwidth}{" + name + "} }\\\\[2pt]\n")
        file.write("\\footnotesize \\truncate{\\textwidth}{" + artist_names + "}\n")
        file.write("\\end{minipage}\\\\[2pt]\n")
        file.write("\n")
    
    def write_artist(artist_ct, artist_db):

        file.write("\\noindent\\LARGE{Top Artist!}\\\\[10pt]\n")
        id = artist_ct['id']
        artist_info = artist_db[id]
        pic_path = get_artist_artwork(id, artist_info['artwork_url'])
        name = artist_info['name']
        artist_names = format_artist_names(artist_info['genres']).title()
        sp_url = artist_info['url']

        # replace latex special characters
        name = replace_latex_special_characters(name)
        artist_names = replace_latex_special_characters(artist_names)

        file.write("\\begin{minipage}{.2\\textwidth}\n")
        file.write("\\href{" + sp_url + "}{\\includegraphics[width = \\textwidth]{" + pic_path + "}}\n")
        file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
        file.write("\\begin{minipage}{.75\\textwidth}\n")
        file.write("\\small \\textbf{\\truncate{\\textwidth}{" + name + "} }\\\\[2pt]\n")
        file.write("\\footnotesize \\truncate{\\textwidth}{" + artist_names + "}\n")
        file.write("\\end{minipage}\\\\[2pt]\n")
        file.write("\n")


    track_cts, artist_cts, album_cts, total_tracks = cts
    track_db, artist_db, album_db = dbs

    # make_plot(track_cts[0], 'track')
    # make_plot(artist_cts[0], 'artist')
    # make_plot(album_cts[0], 'album')

    file.write("\\newpage\n")

    write('track', write_track, track_cts[0], track_db)
    write('artist', write_artist, artist_cts[0], artist_db)
    write('album', write_album, album_cts[0], album_db)
    make_user_stamp(file, usr_info)
    
    file.write("\\newpage\n")

    



def main():
    sp = get_auth()

    yesterday = False
    otherday = ""
    if len(sys.argv) == 2:
        if sys.argv[1] == "y": yesterday = True
        else: 
            otherday = sys.argv[1]
            # TODO: implement a way to standardize adding any date to allow for an analysis for any date
            pass

    # ========== MAKE DATAFRAMES, COUNTS, ETC.

    # get datetime of "today", the day in question
    day = start_of_day_est(datetime.today())

    if yesterday: 
        day = day - timedelta(days = 1)
    elif otherday != "": 
        day = start_of_day_est(parser.parse(otherday))

    # end of day is one day later than the day object
    eod = day + timedelta(days=1)

    # get DTO of the beginning of the current month
    m = int(datetime.strftime(day, "%m"))
    month = day.replace(month = m, day = 1)

    # get a string for the date, e.g. 12-2021
    my = datetime.strftime(day, "%Y-%m")
    month_str = datetime.strftime(month, "%B")
    today_str = datetime.strftime(day,"%B %d, %Y")

    # get relevant series and dfs
    songlist = pd.read_csv(f"{home_path}/data/{my}-songlist.txt")

    # get local song database
    if os.path.exists(f"{home_path}/data/{my}-database.txt"):
        with open(f"{home_path}/data/{my}-database.txt","r") as f:
            dbs = json.loads(f.read()) # track_db, artist_db, album_db
    else: dbs = {},{},{}


    today_df = make_df_range(songlist, day, eod)
    today_cts = get_counts(sp, today_df, dbs)

    month_df = make_df_range(songlist, month, eod)
    month_cts = get_counts(sp, month_df, dbs)

    track_db, artist_db, album_db = dbs

    # ========== WRITE TO FILE

    # user information
    me = sp.current_user()
    display_name = me["display_name"]
    # get profile photo
    pp_path = f'{home_path}/analysis/pp.png'
    urlretrieve(me["images"][0]["url"],pp_path)
    make_image_circular(pp_path,pp_path)
    # get user url
    user_url = me["external_urls"]["spotify"]
    today_usr_info = display_name, user_url, pp_path, today_str


    # textfile
    txt = open(f"{home_path}/analysis/analysis.txt", "w")

    make_top_songs(today_cts, txt, "TODAY'S TOP SONGS", track_db)
    txt.write("\n")
    make_top_songs(month_cts, txt, f"{month_str.upper()}'S TOP SONGS", track_db)

    txt.write(f"\n{display_name}, {today_str}")

    txt.close()


    # pdf
    pdf = open(f"{home_path}/analysis/part.tex", "w")

    if full_summary:
        make_fullpage_summary(pdf, today_cts, dbs, today_usr_info, "Today")
        make_fullpage_summary(pdf, month_cts, dbs, today_usr_info, month_str, pct=True)
        additional_analysis(pdf, dbs, month_cts, today_usr_info, month, eod)
    else:
        today_track_cts, today_artist_cts, today_album_cts, today_total = today_cts
        month_track_cts, month_artist_cts, month_album_cts, month_total = month_cts
        make_formatted_top_songs(today_track_cts, pdf, "Today", today_total, track_db)
        make_formatted_top_songs(month_track_cts, pdf, month_str, month_total, track_db)
        make_user_stamp(pdf, today_usr_info)

    pdf.close()

    # write updated database
    dbs = track_db, artist_db, album_db
    with open(f"{home_path}/data/{my}-database.txt","w") as output:
        output.write(json.dumps(dbs))

    # compile and delete auxillary files
    os.system(f"{pdflatex_path} -output-directory={home_path}/analysis {home_path}/analysis/analysis.tex > {home_path}/analysis/pdflatex_output.txt")
    # delte auxillary files
    os.system(f"rm {home_path}/analysis/analysis.aux")
    os.system(f"rm {home_path}/analysis/analysis.log")
    os.system(f"rm {home_path}/analysis/analysis.out")
    os.system(f"rm {home_path}/analysis/*.png")
    os.system(f"rm {home_path}/analysis/part.tex")
    os.system(f"rm {home_path}/analysis/pdflatex_output.txt")

if __name__ == "__main__":
    main()
