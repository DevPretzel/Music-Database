"""
Filename: addData.py
Created by: Roland Pelzel, Benji Austin, Mark Brahler
Date: 2026-05-19
Database Systems Final Project
Description: This program adds new data into the music database.
"""

from psycopg2 import *
from datetime import datetime
import getpass
import sys

ISRC_COUNTRIES = ["AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AR", "AT",
                  "AU", "AW", "AZ", "BA", "BB", "BC", "BD", "BE", "BF", "BG",
                  "BH", "BI", "BJ", "BM", "BN", "BO", "BS", "BT", "BW", "BY",
                  "BZ", "CA", "CD", "CF", "CG", "CH", "CI", "CL", "CM", "CN",
                  "CO", "CP", "CR", "CS", "CU", "CV", "CW", "CY", "CZ", "DE",
                  "DG", "DK", "EG", "FI", "FR", "GR", "HK", "IN", "IE", "IL", 
                  "IT", "JP", "KE", "KR", "MX", "NL", "NZ", "NO", "PL", "PT", 
                  "RU", "SA", "SG", "ZA", "ES", "SE", "CH", "TH", "TR", "UA", 
                  "AE", "VN", "US", "GB", ]

def main():
    """
    Switches:
      --artist
      --album
      --song
      --name
      --label
      --genre
    """
    
    if len(sys.argv) != 2:
        print("Invalid number of arguments.")
        exit(1)
    
    dbuser = getpass.getuser()
    dbpass = getpass.getpass()
    
    connstr = "host=csdept dbname=cs236proj user=%s password=%s" % \
                (dbuser, dbpass)
    
    try:
        conn = connect(connstr)
    except:
        print("Connection failed.")
        exit(1)
    
    print()
    print("Music Database Rules:")
    print("  Album insertion requires an existing artist and label.")
    print("  Song insertion requires an existing album.")
    print()
    
    try:
        match sys.argv[1]:
            case "--artist":
                insert_artist(conn)
            case "--album":
                insert_album(conn)
            case "--song":
                insert_song(conn)
            case "--name":
                insert_name(conn)
            case "--label":
                insert_label(conn)
            case "--genre":
                insert_genre(conn)
            case _:
                print("Invalid command.")
                exit(1)
    except KeyboardInterrupt:
        conn.close()
        print("\nConnection closed.")
        exit()
    
    conn.close()
    print("Connection closed.")
        

def insert_artist(conn):
    """
    For adding just an artist to the database.
    Requires an artist name and optional real names. 
    Will insert into artists, real_names, and artist_real_names.
    
    :param conn: the database connection object
    """
    # Get the artist/group's name.
    artist_name = input("Enter the artist/group's name: ")
    
    # Get the number of names associated with this artist/group.
    try:
        num = int(
            input(f"How many names are associated with {artist_name}? ")
        )
    except:
        print("Invalid input.")
        return
    
    first_names = []
    last_names  = []
    
    # Get each of the names associated with the artist/group.
    if num:
        for k in range(num):
            print("-----------------------------------------")
            first_names.append(input(f"[{k+1}] Enter their first name: "))
            last_names.append(input(f"[{k+1}] Enter their last name: "))
        print("-----------------------------------------")
    
    artist_query = "INSERT INTO group4.artists (artist_name) " \
                    "VALUES (%s)" \
                    "RETURNING artist_id;"
    
    name_query = "INSERT INTO group4.real_names (first_name, last_name) " \
                    "VALUES (%s, %s)" \
                    "RETURNING name_id;"
    
    a_n_query = \
        "INSERT INTO group4.artist_real_names (artist_id, name_id) " \
        "VALUES (%s, %s);"
    
    # Insert the artist and fetch the artist_id.
    dbcursor = conn.cursor()
    dbcursor.execute(artist_query, (artist_name,))
    artist_id = dbcursor.fetchone()[0]
    
    # Insert the names of the artist/group if they were provided.
    if first_names or last_names:
        for i in range(num):
            dbcursor.execute(name_query, (first_names[i], last_names[i]))
            name_id = dbcursor.fetchone()[0]
            dbcursor.execute(a_n_query, (artist_id, name_id))
    
    conn.commit()
    print("Completed.")


def insert_album(conn):
    """
    For adding an album to the database.
    Requires an album title, one or more artists, a upc, a label name, 
    a release date (YYYY-MM-DD), one or more song titles, isrc info, 
    explicit info, and a genre name. 
    Will insert into albums, songs, genres, labels, artist_albums, and
    album_labels.
    
    :param conn: the database connection object
    """
    # Get the album title.
    album_title = input("Enter an album title: ")
    
    # Get the number of artists associated with the album.
    try:
        num = int(input(
            f"How many artists are associated with {album_title}? "))
    except:
        print("Invalid input.")
        return
    
    # Get the stage names of each artist.
    artists = []
    if num:
        for i in range(num):
            print("-----------------------------------------")
            artists.append(input(f"[{i+1}] Enter the artist name: "))
        print("-----------------------------------------")
    
    # Check that each provided artist exists in the database.
    artist_query = "SELECT artist_id FROM group4.artists " \
                   "WHERE artist_name = %s;"
    dbcursor = conn.cursor()
    artist_ids = []
    for k in range(num):
        dbcursor.execute(artist_query, (artists[k],))
        try:
            fetch = dbcursor.fetchone()[0]
        except:
            print(f"{artists[k]} was not in the database.")
            return
        if not fetch:
            print(f"{artists[k]} does not exist in the database. ")
            return
        artist_ids.append(fetch)
    
    # Get the album's UPC.
    upc = input("Enter the UPC: ")
    if not upc.isdigit() or len(upc) != 12:
        print("Invalid UPC.")
        return
    
    # Get the number of labels associated with the album.
    try:
        numlabels = int(
            input(f"How many labels are associated with {album_title}? "))
    except:
        print("Invalid input.")
        return
    
    # Get each label.
    labels = []
    if numlabels:
        for i in range(numlabels):
            print("-----------------------------------------")
            labels.append(input(f"[{i+1}] Enter the label name: "))
        print("-----------------------------------------")
    
    # Check that each provided label exists in the database.
    label_query = "SELECT label_id FROM group4.labels " \
                   "WHERE label_name = %s;"
    label_ids = []
    for k in range(numlabels):
        dbcursor.execute(label_query, (labels[k],))
        fetch = dbcursor.fetchone()[0]
        if not fetch:
            print(f"{labels[k]} does not exist in the database. ")
            return
        label_ids.append(fetch)
    
    # Get the album's release date.
    release = input("Enter the release date (YYYY-MM-DD): ")
    
    # Check for valid release date.
    if not datetime.strptime(release, "%Y-%m-%d"):
        print("Invalid release date format (it told you the format)")
        return
    
    # Get the number of songs on the album.
    try:
        n = int(input("How many songs are on this album? "))
    except:
        print("Invalid input.")
        return
    
    if not n:
        print("An album must contain at least one song.")
        return
    
    # Get each song's info.
    songs = []
    isrcs = []
    explicit = []
    genres = []
    for j in range(n):
        print("-----------------------------------------")
        songs.append(input(f"[{j+1}] Enter a song name (in order): "))
        isrcs.append(input(f"[{j+1}] Enter its ISRC: "))
        explicit.append(input(
            f"[{j+1}] Does this song contain explicit content (Y/n)? "))
        genres.append(input(f"[{j+1}] Input a genre for the song: "))
        
        # Check input format.
        if not songs[j]:
            songs.pop()
            isrcs.pop()
            explicit.pop()
            genres.pop()
            print("Songs must have a title. Try again.")
            num += 1
            continue
        country = isrcs[j][:2]  # Break down ISRC into its parts.
        registrant = isrcs[j][2:5]
        year = isrcs[j][5:7]
        designation = isrcs[j][7:12]
        if (country.upper() not in ISRC_COUNTRIES or 
            not registrant.isalnum() or
            not year.isdigit() or
            not designation.isdigit()):
            songs.pop()
            isrcs.pop()
            explicit.pop()
            genres.pop()
            n += 1
            print("Invalid ISRC. Try again.")
            continue
        explicit[j] = "true" if explicit[j].lower() == 'y' else "false"
        if not genres[j]:
            print("Songs must have a genre. Try again.")
            n += 1
            continue
        
        genre_query = "INSERT INTO group4.genres (genre_name) " \
                      "VALUES (%s) " \
                      "RETURNING genre_id;"
        song_query = "INSERT INTO group4.songs " \
                     "(song_title, is_explicit, upc, genre_id, isrc_country," \
                     "isrc_registrant, isrc_year, isrc_designation) " \
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        
        # Get the genre_id.
        try:
            dbcursor.execute(genre_query, (genres[j],))
            genre_id = dbcursor.fetchone()[0]
        except:
            conn.rollback()
            genre_select = "SELECT genre_id FROM group4.genres " \
                           "WHERE genre_name = %s;"
            dbcursor.execute(genre_select, (genres[j],))
            genre_id = dbcursor.fetchone()[0]
        
        # With one validated song, the album can now exist.
        if j == 0:
            album_query = "INSERT INTO group4.albums (" \
                          "upc, album_title, release_date) " \
                          "VALUES (%s, %s, %s);"
            a_a_query = "INSERT INTO group4.artist_albums (artist_id, upc) " \
                        "VALUES (%s, %s);"
            a_l_query = "INSERT INTO group4.album_labels (upc, label_id) " \
                        "VALUES (%s, %s);"
            dbcursor.execute(album_query, (upc, album_title, release))
            for k in range(len(artist_ids)):
                dbcursor.execute(a_a_query, (artist_ids[k], upc))
            for l in range(len(label_ids)):
                dbcursor.execute(a_l_query, (upc, label_ids[l]))
        
        # Insert the data.
        dbcursor.execute(song_query, (
            songs[j], explicit[j], upc, genre_id, country, registrant,
            year, designation
        ))
        conn.commit()
    print("-----------------------------------------")
    
    print("Completed.")


def insert_song(conn):
    """
    For adding a song to an album in the database.
    Requires an album title, a genre name, a song title, isrc info,
    and explicit info. 
    Will insert into songs and genres.
    
    :param conn: the database connection object
    """
    # Get the album to add to.
    album = input("Enter the title of the album you're adding to: ")
    album_query = "SELECT album_title, upc FROM group4.albums " \
                  "WHERE album_title = %s;"
    
    # Fetch all albums with that title.
    dbcursor = conn.cursor()
    dbcursor.execute(album_query, (album,))
    albumlist = dbcursor.fetchall()
    if not albumlist:
        print(f"{album} does not exist in the database.")
        return
    
    # Disambiguate if multiple albums exist under that title (unlikely).
    upc = ""
    if len(albumlist) > 1:
        print(f"Found {len(albumlist)} albums under that title.")
        for i in range(len(albumlist)):
            print(albumlist[i])
        upc = input("Which UPC is it: ")
        if not upc.isdigit() or len(upc) != 12:
            print("Invalid input.")
            return
        upc_query = "SELECT album_title FROM group4.albums " \
                    "WHERE upc = %s;"
        dbcursor.execute(upc_query, (upc,))
        if not dbcursor.fetchone()[0]:
            print("UPC was invalid.")
            return
    # Fetch the UPC from the database (so the user doesn't have to know it).
    else:
        upc_query = "SELECT upc FROM group4.albums " \
                    "WHERE album_title = %s"
        dbcursor.execute(upc_query, (album,))
        upc = dbcursor.fetchone()[0]
    
    # Get the number of songs to add to the album. 
    try:
        num = int(
            input("Enter the number of songs you'd like to add: ")
        )
    except:
        print("Invalid input.")
        return
    
    if not num:
        print("Invalid input.")
        return
    
    # Get each song's info.
    songs = []
    isrcs = []
    explicit = []
    genres = []
    for j in range(num):
        print("-----------------------------------------")
        songs.append(input(f"[{j+1}] Enter a song name (in order): "))
        isrcs.append(input(f"[{j+1}] Enter its ISRC: "))
        explicit.append(input(
            f"[{j+1}] Does this song contain explicit content (Y/n)? "))
        genres.append(input(f"[{j+1}] Input a genre for the song: "))
        
        # Check input format.
        if not songs[j]:
            songs.pop()
            isrcs.pop()
            explicit.pop()
            genres.pop()
            print("Songs must have a title. Try again.")
            num += 1
            continue
        country = isrcs[j][:2]  # Break down ISRC into its parts.
        registrant = isrcs[j][2:5]
        year = isrcs[j][5:7]
        designation = isrcs[j][7:12]
        if (country.upper() not in ISRC_COUNTRIES or 
            not registrant.isalnum() or
            not year.isdigit() or
            not designation.isdigit()):
            songs.pop()
            isrcs.pop()
            explicit.pop()
            genres.pop()
            num += 1
            print("Invalid ISRC. Try again.")
            continue
        explicit[j] = "true" if explicit[j].lower() == 'y' else "false"
        if not genres[j]:
            print("Songs must have a genre. Try again.")
            num += 1
            continue
        
        genre_query = "INSERT INTO group4.genres (genre_name) " \
                      "VALUES (%s) " \
                      "RETURNING genre_id;"
        song_query = "INSERT INTO group4.songs " \
                     "(song_title, is_explicit, upc, genre_id, isrc_country," \
                     "isrc_registrant, isrc_year, isrc_designation) " \
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        
        # Get the genre_id.
        try:
            dbcursor.execute(genre_query, (genres[j],))
            genre_id = dbcursor.fetchone()[0]
        except:
            conn.rollback()
            genre_select = "SELECT genre_id FROM group4.genres " \
                           "WHERE genre_name = %s;"
            dbcursor.execute(genre_select, (genres[j],))
            genre_id = dbcursor.fetchone()[0]
        
        # Insert the data.
        dbcursor.execute(song_query, (
            songs[j], explicit[j], upc, genre_id, country, registrant,
            year, designation
        ))
        conn.commit()
    print("-----------------------------------------")
    
    print("Completed.")
    

def insert_name(conn):
    """
    For adding a name to the database.
    Requires at least a first or last name and an associated artist name.
    Will insert into real_names and artist_real_names.
    
    :param conn: the database connection object
    """
    # Get the artist/group that the name(s) will be associated with.
    artist_name = input("Enter the artist/group name: ")
    artist_query = "SELECT * FROM group4.artists " \
                   "WHERE artist_name = %s;"
    
    # Fetch the provided artist name. 
    dbcursor = conn.cursor()
    dbcursor.execute(artist_query, (artist_name,))
    existing_artist = dbcursor.fetchall()
    
    # Check that the artist exists in the database.
    if not existing_artist:
        print(f"{artist_name} does not exist in the database. ")
        return
    
    # Get the number of names associated with the artist/group.
    try:
        num = int(
            input(f"How many names are associated with {artist_name}? ")
        )
    except:
        print("Invalid input.")
        exit(1)
    
    if not num:
        print("Why'd you even run this command then?")
        return
    
    first_names = []
    last_names  = []
    
    # Get the names associated with the artist/group.
    for i in range(num):
        print("-----------------------------------------")
        first_names.append(input(f"[{i+1}] Enter their first name: "))
        last_names.append(input(f"[{i+1}] Enter their last name: "))
    print("-----------------------------------------")
    
    name_query = "INSERT INTO group4.real_names (first_name, last_name) " \
                    "VALUES (%s, %s)" \
                    "RETURNING name_id;"
    
    a_n_query = \
        "INSERT INTO group4.artist_real_names (artist_id, name_id) " \
        "VALUES (%s, %s);"
    
    dbcursor = conn.cursor()
    
    # Insert the names into the database.
    if first_names or last_names:
        for j in range(num):
            dbcursor.execute(name_query, (first_names[j], last_names[j]))
            name_id = dbcursor.fetchone()[0]
            dbcursor.execute(a_n_query, (existing_artist[0][0], name_id))
    
    conn.commit()
    print("Completed.")
    

def insert_label(conn):
    """
    For adding a label to the database.
    Requires a label name.
    Will insert into labels. 
    
    :param conn: the database connection object
    """
    # Get the label name.
    label = input("Enter a label: ")
        
    label_query = "INSERT INTO group4.labels (label_name) " \
                    "VALUES (%s)"
    
    dbcursor = conn.cursor()
    
    # Insert the label into the database.
    try:
        dbcursor.execute(label_query, (label,))
    except:
        print(f"{label} already exists.")
        return
    
    conn.commit()
    print("Completed.")


def insert_genre(conn):
    """
    For adding a genre to the database.
    Requires a genre name. 
    Will insert into genres. 
    
    :param conn: the database connection object
    """
    # Get the genre.
    genre = input("Enter a genre: ")
        
    genre_query = "INSERT INTO group4.genres (genre_name) " \
                    "VALUES (%s)"
    
    dbcursor = conn.cursor()
    
    # Insert the genre into the database.
    try:
        dbcursor.execute(genre_query, (genre,))
    except:
        print(f"{genre} already exists.")
        exit(1)
    
    conn.commit()
    print("Completed.")


main()