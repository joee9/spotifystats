# Joe Nyhan, 07 March 2022
# Latex related functions; mainly sourced, at least now, from analysis.py

import os
import numpy as np
from urllib.request import urlretrieve
from PIL import Image, ImageDraw, ImageFilter

from secrets import home_path


def replace_latex_special_characters(string):

    if "&" in string: string = string.replace("&", "\&")
    if "$" in string: string = string.replace("$", "\$")
    if "#" in string: string = string.replace("#", "\#")
    if "%" in string: string = string.replace("%", "\%")
    # if "\\" in string: string = string.replace("\\", "\\\\")

    return string

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

        name = replace_latex_special_characters(name)
        artist_names = replace_latex_special_characters(artist_names)

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
