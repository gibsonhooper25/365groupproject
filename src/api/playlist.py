import sqlalchemy
from fastapi import APIRouter, Depends
from src.api import auth, song
from src import database as db
from sqlalchemy.exc import DBAPIError
from sqlalchemy import *
from pydantic import BaseModel
from .user import log_in, LogIn

router = APIRouter(
    prefix="/playlists",
    tags=["playlists"],
    dependencies=[Depends(auth.get_api_key)],
)


#Creates playlist for the user with the given title, mood, and length
#Finds (length) number of songs randomly from query of all songs with (mood)
@router.post("/new/curated")
def create_curated_playlist(user_id: int, title: str, mood: song.Mood, length: int):
    sql_to_execute = """
    SELECT mood_songs.song as id FROM mood_songs
    WHERE mood = :mood
    ORDER BY RANDOM()
    LIMIT :length 
    """
    try:
        with db.engine.begin() as connection:
            get_id = connection.execute(sqlalchemy.text("""
                INSERT INTO playlists (creator_id, title, mood)
                VALUES (:user_id, :title, :mood)
                RETURNING id
            """), [{"user_id": user_id, "title": title, "mood": mood}])
            id = get_id.first().id

            result = connection.execute(sqlalchemy.text(sql_to_execute), 
                    [{"mood": mood, "length": length}])
            for row in result:
                sql_to_execute = """
                    INSERT INTO playlist_songs (playlist_id, song_id)
                    VALUES (:playlist_id, :song_id)
                """
                connection.execute(sqlalchemy.text(sql_to_execute), 
                    [{"playlist_id": id, "song_id": row.id}])
            return {"playlist": id}

    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"


class NewPlaylist(BaseModel):
    username: str
    password: str
    playlist_name: str
    mood: song.Mood


#creates an empty playlist with the given playlist name and mood
#username and password must be authenticated to create
@router.post("/new/personal")
def create_personal_playlist(playlist_info: NewPlaylist):
    try:
        with db.engine.begin() as connection:
            user_id_query = "SELECT id, password FROM users WHERE username = :given_uname AND user_type != 'artist'"
            user_id_query_result = connection.execute(sqlalchemy.text(user_id_query), [{"given_uname": playlist_info.username}]).first()
            if not user_id_query_result:
                return "No listener exists for the given username"
            credentials = LogIn(username=playlist_info.username, password=playlist_info.password)
            if log_in(credentials) != "ok":
                return "Incorrect password"
            insert_query = "INSERT INTO playlists (creator_id, title, mood) VALUES (:cid, :title, :mood) RETURNING id"
            new_playlist_id = connection.execute(sqlalchemy.text(insert_query), [{"cid": user_id_query_result.id, "title": playlist_info.playlist_name, "mood": playlist_info.mood}]).scalar()
        return {"playlist": new_playlist_id}
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

#adds song with given id to playlist with given id.
# Shows error message if one or both ids do not correspond to any record. Currently, does not allow same song to be in playlist twice.
@router.post("/{playlist_id}/add-song/{song_id}")
def add_song_to_playlist(playlist_id: int, song_id: int):
    try:
        with db.engine.begin() as connection:
            #check if the playlist exists, return if it doesn't
            playlist_query = "SELECT id FROM playlists WHERE id = :pid"
            pid = connection.execute(sqlalchemy.text(playlist_query), [{"pid": playlist_id}]).first()
            if not pid:
                return "No playlist exists for the given playlist ID"

            #check if the song exists, return if it doesn't
            song_query = "SELECT id FROM songs WHERE id = :sid"
            sid = connection.execute(sqlalchemy.text(song_query), [{"sid": song_id}]).first()
            if not sid:
                return "No song exists for the given song ID"
            
            #add entry to playlist_songs
            insert_query = "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (:pid, :sid)"
            connection.execute(sqlalchemy.text(insert_query), [{"pid": playlist_id, "sid": song_id}])
            return "Song added to playlist"
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

#adds all songs from a given album to a playlist with given id. Error message if album does not exist
@router.post("/{playlist_id}/add-songs/{album_id}")
def add_album_songs_to_playlist(playlist_id: int, album_id: int):
    sql_to_execute = """
    SELECT songs.id FROM albums
    JOIN songs ON album_id = albums.id
    WHERE album_id = :album_id
    """
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql_to_execute), 
                    [{"album_id": album_id}])
            album_exists = False
            for row in result:
                album_exists = True
                sql_to_execute = """
                    INSERT INTO playlist_songs (playlist_id, song_id)
                    SELECT :playlist_id, :song_id
                    WHERE NOT EXISTS (
                        SELECT *
                        FROM playlist_songs
                        WHERE playlist_id = :playlist_id and song_id = :song_id
                    )
                """
                connection.execute(sqlalchemy.text(sql_to_execute), 
                    [{"playlist_id": playlist_id, "song_id": row.id}])
            if album_exists:
                return "No album exists for the given album ID"
            return "Added album to playlist"

    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

#deletes single song from playlist. Shows error message if playlist does not exist or song was not in playlist
@router.delete("/{playlist_id}/remove-song/{song_id}")
def delete_song_from_playlist(playlist_id: int, song_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                DELETE FROM playlist_songs
                WHERE playlist_id = :playlist_id AND song_id = :song_id 
            """),
            [{"playlist_id": playlist_id, "song_id": song_id}])
        if result.rowcount == 0:
            return "Song not removed, either no playlist exists for the given playlist ID or no song exists for the given song ID "
             
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

    return "Removed song from playlist"

@router.get("/{playlist_id}")
def get_playlist(playlist_id: int):
    sql_to_execute = """
    SELECT title, genre, duration
    FROM songs
    JOIN playlist_songs ON playlist_songs.song_id = songs.id
    WHERE playlist_songs.playlist_id = :playlist_id
    """
    try:
        with db.engine.begin() as connection:
            playlist = connection.execute(sqlalchemy.text(sql_to_execute), [{"playlist_id": playlist_id}])
            song_list = []
            for song in playlist:
                song_list.append({
                    "title": song.title,
                    "genre": song.genre,
                    "duration_seconds": song.duration
                })
            if not song_list:
                return "No playlist exists for the given playlist ID"
            return song_list
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
