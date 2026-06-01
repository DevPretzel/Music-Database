"""
Filename: update.py
Created by: Roland Pelzel, Benji Austin, Mark Brahler
Date: 2026-05-19
Database Systems Final Project
Description: This program updates data in the music database.
"""

from psycopg2 import *
import getpass
import sys

def main():
    """
    Switches:
      --artist
      --album
      --song
      --name
      --label
      --genre
      --streams
      --downloads
      --favorites
      --explicit
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
    print("  Data must exist in the database to be updated.")
    print()
    
    try:
        match sys.argv[1]:
            case "--artist":
                update_artist(conn)
            case "--album":
                update_album(conn)
            case "--song":
                update_song(conn)
            case "--name":
                update_name(conn)
            case "--label":
                update_label(conn)
            case "--genre":
                update_genre(conn)
            case "--streams":
                update_streams(conn)
            case "--downloads":
                update_downloads(conn)
            case "--favorites":
                update_favorites(conn)
            case "--explicit":
                update_explicit(conn)
            case _:
                print("Invalid command.")
                exit(1)
    except KeyboardInterrupt:
        conn.close()
        print("\nConnection closed.")
        exit()
    
    conn.close()
    print("Connection closed.")
    

def update_artist(conn):
    """
    For updating an artist name in the database.
    Requires the artist to exist in the database.
    Will update artists table.
    
    :param conn: the database connection object
    """
    # Get the artist/group's name.
    artist_name = input("Enter the artist/group's name: ")
    new_name = input(f"Enter the updated name for {artist_name}: ")
    
    # Exit if name doesn't change.
    if artist_name == new_name:
        print("Artist name did not change.")
        return
    
    artist_query = "UPDATE group4.artists " \
                    "SET artist_name = %s " \
                    "WHERE artist_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(artist_query, (new_name, artist_name))
    
    if not dbcursor.rowcount:
        print(f"{artist_name} does not exist in the database.")
    else:
        print(f"{artist_name} changed to {new_name}.")
        conn.commit()


def update_album(conn):
    """
    For updating an album title in the database.
    Requires the album to exist in the database.
    Will update albums table.
    
    :param conn: the database connection object
    """    
    # Get the album name.
    album_name = input("Enter the album title: ")
    artist_name = input("Enter its artist/group's name: ")
    new_name = input("Enter the new album title: ")
    
    # Exit if name doesn't change.
    if album_name == new_name:
        print("Album title did not change.")
        return
    
    album_query = "UPDATE group4.albums " \
                    "SET album_title = %s " \
                    "FROM group4.artist_albums " \
                    "JOIN group4.artists " \
                    "ON artists.artist_id = artist_albums.artist_id " \
                    "WHERE albums.upc = artist_albums.upc " \
                        "AND albums.album_title = %s " \
                        "AND artists.artist_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(album_query, (new_name, album_name, artist_name))
    
    if not dbcursor.rowcount:
        print(f"{artist_name} does not have an album called {album_name}.")
    else:
        print(f"{album_name} by {artist_name} changed to {new_name}.")
        conn.commit()


def update_song(conn):
    """
    For updating a song title in the database.
    Requires the artist and album to exist in the database.
    Will update songs table.
    
    :param conn: the database connection object
    """    
    # Get the song title.
    song_name = input("Enter the song title: ")
    album_name = input(f"Enter the album {song_name} is on: ")
    artist_name = input(f"Enter the artist associated with {album_name}: ")
    new_name = input(f"Enter the new name for {song_name}: ")
    
    # Exit if title doesn't change.
    if song_name == new_name:
        print("Song title did not change.")
        return
    
    song_query = "UPDATE group4.songs " \
                    "SET song_title = %s " \
                    "FROM group4.albums " \
                    "JOIN group4.artist_albums " \
                    "ON albums.upc = artist_albums.upc " \
                    "JOIN group4.artists " \
                    "ON artist_albums.artist_id = artists.artist_id " \
                    "WHERE songs.upc = albums.upc " \
                        "AND songs.song_title = %s " \
                        "AND albums.album_title = %s " \
                        "AND artists.artist_name = %s;"
    
    # Execute query
    dbcursor = conn.cursor()
    dbcursor.execute(song_query, (new_name, song_name, album_name, artist_name))
    
    if not dbcursor.rowcount:
        print(f"{song_name} by {artist_name} on {album_name} does not exist.")
    else:
        print(f"Changed {song_name} by {artist_name} to {new_name}.")
        conn.commit()


def update_name(conn):
    """
    For updating an artist name in the database.
    Requires the artist to exist in the database.
    Will update names table.
    
    :param conn: the database connection object
    """    
    # Get the artist/group's name.
    artist_name = input("Enter the artist/group's name: ")
    first = input("Enter the first name of who you want to change: ")
    last  = input("Enter the last name of who you want to change: ")
    space = ' ' if first and last else ''
    new_first = input(f"Enter the new first name for {first+space+last}: ")
    new_last  = input(f"Enter the new last name for {first+space+last}: ")
    
    name_query = "UPDATE group4.real_names " \
                    "SET first_name = %s, last_name = %s " \
                    "FROM group4.artist_real_names " \
                    "JOIN group4.artists " \
                    "ON artists.artist_id = artist_real_names.artist_id " \
                    "WHERE real_names.name_id = artist_real_names.name_id " \
                        "AND artists.artist_name = %s " \
                        "AND real_names.first_name = %s " \
                        "AND real_names.last_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(
        name_query, (
            new_first, new_last, artist_name, first, last
        )
    )
    
    if not dbcursor.rowcount:
        print(f"That name is not associated with {artist_name}.")
    else:
        ns = ' ' if new_first and new_last else ''
        print(f"{first+space+last} changed to {new_first+ns+new_last}")
        conn.commit()


def update_label(conn):
    """
    For updating a label name in the database.
    Requires the label to exist in the database.
    Will update labels table.
    
    :param conn: the database connection object
    """    
    # Get the label name.
    label_name = input("Enter the label name you would like to change: ")
    new_name = input("Enter the label's new name: ")
    
    # Exit if name doesn't change.
    if label_name == new_name:
        print("Label name did not change.")
        return
    
    artist_query = "UPDATE group4.labels " \
                    "SET label_name = %s " \
                    "WHERE label_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(artist_query, (new_name, label_name))
    
    if not dbcursor.rowcount:
        print(f"{label_name} does not exist in the database.")
    else:
        print(f"{label_name} changed to {new_name}.")
        conn.commit()


def update_genre(conn):
    """
    For updating genre info in the database.
    Requires the artist and album to exist in the database.
    Will update songs table.
    
    :param conn: the database connection object
    """
    # Get the song name.
    song_name = input("Enter the song title: ")
    album_name = input("Enter the title of the album it's on: ")
    artist_name = input("Enter the artist: ")
    genre = input(f"Enter the genre for {song_name}: ").strip()
    
    id_query = "SELECT genre_id FROM group4.genres " \
                "WHERE genre_name = %s;"
    genre_query = "UPDATE group4.songs " \
                    "SET genre_id = %s " \
                    "FROM group4.albums " \
                    "JOIN group4.artist_albums " \
                    "ON albums.upc = artist_albums.upc " \
                    "JOIN group4.artists " \
                    "ON artist_albums.artist_id = artists.artist_id " \
                    "WHERE songs.upc = albums.upc " \
                        "AND songs.song_title = %s " \
                        "AND albums.album_title = %s " \
                        "AND artists.artist_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(id_query, (genre,))
    id = dbcursor.fetchall()
    if not id:
        print(f"{genre} does not exist in the database.")
        return
    dbcursor.execute(
        genre_query, (
            id[0][0], song_name, album_name, artist_name
        )
    )
    
    if not dbcursor.rowcount:
        print(f"{song_name} by {artist_name} on {album_name} doesn't exist.")
    else:
        print(f"Genre of {song_name} by {artist_name} updated to {genre}.")
        conn.commit()


def update_streams(conn):
    """
    For updating stream info in the database.
    Requires the artist and album to exist in the database.
    Will update songs table.
    
    :param conn: the database connection object
    """
    # Get the song name.
    song_name = input("Enter the song title: ")
    album_name = input("Enter the title of the album it's on: ")
    artist_name = input("Enter the artist: ")
    streams = input("Enter the number of streams to add: ").strip()
    
    if not streams.isdigit():
        print("Invalid input.")
        return
    if not int(streams):
        print("Invalid input.")
        return
    
    stream_query = "UPDATE group4.songs " \
                    "SET streams = streams + %s " \
                    "FROM group4.albums " \
                    "JOIN group4.artist_albums " \
                    "ON albums.upc = artist_albums.upc " \
                    "JOIN group4.artists " \
                    "ON artist_albums.artist_id = artists.artist_id " \
                    "WHERE songs.upc = albums.upc " \
                        "AND songs.song_title = %s " \
                        "AND albums.album_title = %s " \
                        "AND artists.artist_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(
        stream_query, (
            streams, song_name, album_name, artist_name
        )
    )
    
    if not dbcursor.rowcount:
        print(f"{song_name} by {artist_name} on {album_name} doesn't exist.")
    else:
        print(f"{streams} streams added to {song_name} by {artist_name}.")
        conn.commit()


def update_downloads(conn):
    """
    For updating downloads info in the database.
    Requires the artist and album to exist in the database.
    Will update songs table.
    
    :param conn: the database connection object
    """    
    # Get the song name.
    song_name = input("Enter the song title: ")
    album_name = input("Enter the title of the album it's on: ")
    artist_name = input("Enter the artist: ")
    downloads = input("Enter the number of downloads to add: ").strip()
    
    if not downloads.isdigit():
        print("Invalid input.")
        return
    if not int(downloads):
        print("Invalid input.")
        return
    
    download_query = "UPDATE group4.songs " \
                    "SET downloads = downloads + %s " \
                    "FROM group4.albums " \
                    "JOIN group4.artist_albums " \
                    "ON albums.upc = artist_albums.upc " \
                    "JOIN group4.artists " \
                    "ON artist_albums.artist_id = artists.artist_id " \
                    "WHERE songs.upc = albums.upc " \
                        "AND songs.song_title = %s " \
                        "AND albums.album_title = %s " \
                        "AND artists.artist_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(
        download_query, (
            downloads, song_name, album_name, artist_name
        )
    )
    
    if not dbcursor.rowcount:
        print(f"{song_name} by {artist_name} on {album_name} doesn't exist.")
    else:
        print(f"{downloads} downloads added to {song_name} by {artist_name}.")
        conn.commit()


def update_favorites(conn):
    """
    For updating favorites info in the database.
    Requires the artist and album to exist in the database.
    Will update songs table.
    
    :param conn: the database connection object
    """    
    # Get the song name.
    song_name = input("Enter the song title: ")
    album_name = input("Enter the title of the album it's on: ")
    artist_name = input("Enter the artist: ")
    favorites = input("Enter the number of favorites to add: ").strip()
    
    if not favorites.isdigit():
        print("Invalid input.")
        return
    if not int(favorites):
        print("Invalid input.")
        return
    
    fav_query = "UPDATE group4.songs " \
                    "SET favorites = favorites + %s " \
                    "FROM group4.albums " \
                    "JOIN group4.artist_albums " \
                    "ON albums.upc = artist_albums.upc " \
                    "JOIN group4.artists " \
                    "ON artist_albums.artist_id = artists.artist_id " \
                    "WHERE songs.upc = albums.upc " \
                        "AND songs.song_title = %s " \
                        "AND albums.album_title = %s " \
                        "AND artists.artist_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(
        fav_query, (
            favorites, song_name, album_name, artist_name
        )
    )
    
    if not dbcursor.rowcount:
        print(f"{song_name} by {artist_name} on {album_name} doesn't exist.")
    else:
        print(f"{favorites} favorites added to {song_name} by {artist_name}.")
        conn.commit()


def update_explicit(conn):
    """
    For updating explicit info in the database.
    Requires the artist and album to exist in the database.
    Will update songs table.
    
    :param conn: the database connection object
    """    
    # Get the song name.
    song_name = input("Enter the song title: ")
    album_name = input("Enter the title of the album it's on: ")
    artist_name = input("Enter the artist: ")
    isexplicit = input("Is the song explicit (Y/n)? ").strip()
    
    if isexplicit.lower() != 'y' and isexplicit.lower() != 'n':
        print("Invalid input.")
        return
    
    isexplicit = True if isexplicit == 'y' else False
    
    stream_query = "UPDATE group4.songs " \
                    "SET is_explicit = %s " \
                    "FROM group4.albums " \
                    "JOIN group4.artist_albums " \
                    "ON albums.upc = artist_albums.upc " \
                    "JOIN group4.artists " \
                    "ON artist_albums.artist_id = artists.artist_id " \
                    "WHERE songs.upc = albums.upc " \
                        "AND songs.song_title = %s " \
                        "AND albums.album_title = %s " \
                        "AND artists.artist_name = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(
        stream_query, (
            isexplicit, song_name, album_name, artist_name
        )
    )
    
    if not dbcursor.rowcount:
        print(f"{song_name} by {artist_name} on {album_name} doesn't exist.")
    else:
        print(f"Explicit status for {song_name} by {artist_name} updated.")
        conn.commit()

main()