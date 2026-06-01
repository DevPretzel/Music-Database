"""
Filename: report.py
Created by: Roland Pelzel, Benji Austin, Mark Brahler
Date: 2026-05-19
Database Systems Final Project
Description: This program reports select data from the music database.
"""

from psycopg2 import *
import getpass
import sys

def main():
    
    """
    Switches:
      --explicit
      (Prints song titles and whether each is explicit or not)
      --downloads
      (Prints song titles and their associated downloads ranking for a specific artist)
      --album-streams
      --artist-streams
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
    
    try:
        match sys.argv[1]:
            case "--explicit":
                explicit(conn)
            case "--downloads":
                downloads(conn)
            case "--album-streams":
                album_streams(conn)
            case "--artist-streams":
                artist_streams(conn)
            case _:
                print("Invalid command.")
                exit(1)
    except KeyboardInterrupt:
        conn.close()
        print("\nConnection closed.")
        exit()
    
    conn.close()
    print("Connection closed.")  
    

def explicit(conn):
    
    # Print header.
    print("A report of song titles and whether each is explicit or not")
    print()    
    
    song = input("Enter a song title: ")
    
    query = "SELECT song_title, is_explicit FROM group4.songs " \
                    "WHERE song_title = %s;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(query, (song,))
    
    # Fetch and print.
    recordList = dbcursor.fetchall()
    for record in recordList:
        print("%-255s %-5s" % record)
            
    dbcursor.close()    


def downloads(conn):
    # Print header.
    print("A report of song titles and their " \
            "associated downloads ranking for an artist")
    print()
    
    artist = input("Enter the name of the artist: ")
    print()
    
    query = "SELECT song_title, downloads " \
            "FROM group4.artists " \
            "JOIN group4.artist_albums " \
            "ON artists.artist_id = artist_albums.artist_id " \
            "JOIN group4.songs " \
            "ON artist_albums.upc = songs.upc " \
            "WHERE artists.artist_name = %s " \
            "ORDER BY downloads DESC;"
    
    # Execute query.
    dbcursor = conn.cursor()
    dbcursor.execute(query, (artist,)) 
    
    # Fetch and print.
    recordList = dbcursor.fetchall()
    if not recordList:
        print(f"No songs found for artist: {artist}")
    else:
        for record in recordList:
            print("%-255s %-15s" % record)
            
    dbcursor.close()


def album_streams(conn):
    """
    Derive the total album streams for a particular album.
    
    :param conn: connection object
    :param artist: string name of the artist whose album the user wants
    """
    album = input("Enter the name of the album: ")
    artist = input("Enter the name of the artist: ")
    
    query = "SELECT SUM(streams) AS album_streams " \
            "FROM group4.artists " \
            "JOIN group4.artist_albums " \
            "ON artists.artist_id = artist_albums.artist_id " \
            "JOIN group4.albums ON artist_albums.upc = albums.upc " \
            "JOIN group4.songs ON albums.upc = songs.upc " \
            "WHERE artists.artist_name = %s " \
            "AND albums.album_title = %s;"
    
    dbcursor = conn.cursor()
    
    try:
        dbcursor.execute(query, (artist, album))
        data = dbcursor.fetchone()[0]
    except:
        print("Query failed.")
        dbcursor.close()
        return
        
    if data is None:
        print(f"No streaming data found for {album} by {artist}.")
        dbcursor.close()
        return
    
    print(f"{album} by {artist}: {data} total streams.")
    dbcursor.close()


def artist_streams(conn):
    """
    Derive the total artist streams from an artist's total album streams.
    
    :param conn: connection object
    :param artist: string name of the artist
    """
    artist = input("Enter the artist: ")
    
    query = "SELECT SUM(streams) AS artist_streams " \
            "FROM group4.artists " \
            "JOIN group4.artist_albums " \
            "ON artists.artist_id = artist_albums.artist_id " \
            "JOIN group4.songs ON artist_albums.upc = songs.upc " \
            "WHERE artists.artist_name = %s;"
    
    dbcursor = conn.cursor()
    
    try:
        dbcursor.execute(query, (artist,))
        data = dbcursor.fetchone()[0]
    except:
        print("Query failed.")
        dbcursor.close()
        return
        
    if data is None:
        print(f"No streaming data found for {artist}.")
        dbcursor.close()
        return
    
    print(f"{artist}: {data} total streams.")
    dbcursor.close()

main()