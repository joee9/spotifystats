# Joe Nyhan, 31 March 2022
# old code for plots; not currently implemented

def additional_analysis(file, dbs, cts, usr_info, month, day):

    bins = []
    for d in range((day-month).days+1):
        bins.append(month+timedelta(days=d))

    def make_plot(info, name):
        parsed_ts = [parser.parse(t).astimezone(est) for t in info['timestamps']]
        # print(parsed_ts)

        # num_bins = (parsed_ts[-1] - parsed_ts[0]).days + 1
        # print(num_bins)
        # print(num_days)
        # print(day,month)
        
        n, a_bins, patches = plt.hist(parsed_ts, bins)
        # n, bin_edges = np.histogram(parsed_ts, bins)
        # plt.bar(bins, n, align='center')

        locs, labels = plt.xticks()
        new_labels = []
        new_locs = []
        first_date = month

        delta = locs[1]-locs[0]
        for i in range(len(locs)):
            l = timedelta(days = delta*i) + first_date
            nl = delta*i + locs[0]
            lf = f'{l:%b %d}'
            new_labels.append(lf)
            new_locs.append(nl)

        plt.xticks(new_locs, new_labels)
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

    
