#!python3
# Simple script for placing TV shows / movies into their proper folders
import os
import glob
import shutil
import re
#TODO: Check if file is in use by bittorrent before moving

DIRLIST = [d for d in os.listdir('.') if os.path.isdir(os.path.join('.', d))]
DIRLOWER = [d.lower() for d in DIRLIST]

# possible naming schemes
re.I = True
PATTERNS = ['s(\d+)e(\d+)', '(\d+)x(\d+)', 'season.(\d+).*episode.(\d+)',
            '(\d)(\d\d)', '(\d\d)(\d\d)']
FILETYPES = ['mkv', 'avi', 'mp4', '3gp']


def videos_in_dir(vdir):
    vdir = globsafe(vdir)
    filelist = []
    for ftype in FILETYPES:
        filelist += glob.glob(os.path.join(vdir, '*.' + ftype))

    return filelist


def normalize_showname(showname):
    showname = showname.lower().replace('.', ' ')[2:]
    return showname.lower().replace('_', ' ')


# Just returns a match for any of the above patterns
def match_patterns(fname):
    for patt in PATTERNS:  # Try all our patterns to get a match
        match = re.search(patt.lower(), fname.lower())
        if match:
            return match


def globsafe(dirname):
    return re.sub(r'(\[|\])', r'[\1]', dirname)


def dir_has_name_like_show(showname, dirlist):
    for dirname in dirlist:
        if dirname in showname:
            return dirname
        if dirname in showname.replace(' ', ''):
            return dirname
        if dirname in showname.replace('_', ' '):
            return dirname
    return False


def move_matches_in_dir(searchpath):
    for fname in videos_in_dir(searchpath):
        # Check if one of the destination directories has a name like our show
        name = dir_has_name_like_show(normalize_showname(fname), DIRLOWER)
        if not name:
            continue

        match = match_patterns(fname)
        # Only do the actual moving if there was a match at some point
        if match:
            season = match.group(1)
            episode = match.group(2)
            print("Moving {0} season {1} episode {2}".format(name, season,
                                                             episode))
            season = int(season)  # Get rid of zeros
            finalpath = os.path.join(name, "Season " + str(season))
            if not "Season " + str(season) in os.listdir(name):
                os.mkdir(finalpath)

            shutil.move(fname, finalpath)

# First we move all the matches just sitting in root of videos
move_matches_in_dir(".")

# Then move any matches in candidate matching dirs, and delete them afterwards
matching_dirs = [(match_patterns(d), d) for d in DIRLIST]
matching_dirs = [(m.string, d) for m, d in matching_dirs if m]
parent_dirs = [d for d in DIRLOWER if d not in [md for md, _ in matching_dirs]]
delete_these = list()
for md, od in matching_dirs:
    if dir_has_name_like_show(md, parent_dirs):
        move_matches_in_dir(od)
        delete_these.append(od)

if delete_these:
    print("Will delete {}\nConfirm? (y/n)".format(delete_these))
    yes = {'yes', 'y', 'ye', ''}
    choice = input().lower()
    if choice in yes:
        for od in delete_these:
            shutil.rmtree(od)
