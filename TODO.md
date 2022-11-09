## get_rp.py
- implement a "temporary" file, where the songs that are still within the 50 recently played songs are kept. Then, when getting new songs, compare to the database of "previously" cataloged songs, and add the ones that have left the 50 song buffer. Then calculate and update a dictionary, called `yyyy-mm-counts.txt`, that contains the current dictiionary counts for that month. Therefore, when getting counts, you only have to analyze the 50 most recently played songs and combine them with the stored counts and resort. This will be faster. Also, allows for counts to be combined for the year and sorted as opposed to just recalculated each day.
- create a "counts" file for each month that is no longer being appended to; use os.path.getmtime() to get the time stamp of each file, then convert to datetime object using datetime.fromtimestamp(). Then, if more than 24 hours since last modification (i.e. old month), create a file and write the counts from that month there. Then, counts won't need to be re calculated each day. Check each month file to see if modification is outside the window, and if so, see if count file (counts dictionary written to json) exists.
- have a way to determine whether to write to previous month based upon modified timestamp.

## structs.py

- figure out a way to sort by name for top music list.