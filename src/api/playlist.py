import sqlalchemy
from fastapi import APIRouter, Depends
from src.api import auth, song
from src import database as db
from sqlalchemy.exc import DBAPIError
from pydantic import BaseModel


router = APIRouter(
    prefix="/playlists",
    tags=["playlists"],
    dependencies=[Depends(auth.get_api_key)],
)

metadata_obj = sqlalchemy.MetaData()
playlists = sqlalchemy.Table("playlists", metadata_obj, autoload_with=db.engine)
playlist_songs = sqlalchemy.Table("playlist_songs", metadata_obj, autoload_with=db.engine)
songs = sqlalchemy.Table("songs", metadata_obj, autoload_with=db.engine)
listeners = sqlalchemy.Table("listeners", metadata_obj, autoload_with=db.engine)
artists = sqlalchemy.Table("artists", metadata_obj, autoload_with=db.engine)

@router.post("/new/curated")
def create_curated_playlist(user_id: int, title: str, mood: song.Mood, length: int):
    sql_to_execute = """
    SELECT songs.id FROM songs
    JOIN mood_songs ON songs.id = mood_songs.song
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
            return {"Playlist": id}

    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"


class NewPlaylist(BaseModel):
    listener: bool #true if listener, false if artist - used for mapping to account name
    email: str
    password: str
    name: str
    mood: song.Mood

@router.post("/new/personal")
def create_personal_playlist(playlist_info: NewPlaylist):
    try:
        if playlist_info.listener:
            user_search_table = listeners
        else:
            user_search_table = artists
        with db.engine.begin() as connection:
            user_id_query = sqlalchemy.select(user_search_table.c.id, user_search_table.c.password).where(user_search_table.c.email == playlist_info.email)
            user_id_query_result = connection.execute(user_id_query).first()
            user_id = user_id_query_result.id
            password = user_id_query_result.password
            if not user_id:
                return "No user exists for the given email"
            if password != playlist_info.password:
                return "Incorrect password"
            insert_query = sqlalchemy.insert(playlists).values(creator_id=user_id, title=playlist_info.name, mood=playlist_info.mood).returning(playlists.c.id)
            new_playlist_id = connection.execute(insert_query).first().id
        return {"Playlist": new_playlist_id}
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

@router.post("/{playlist_id}/add-song/{song_id}")
def add_song_to_playlist(playlist_id: int, song_id: int):
    try:
        with db.engine.begin() as connection:
            #check if the playlist exists, return if it doesn't
            playlist_query = sqlalchemy.select(playlists.c.id).where(playlists.c.id == playlist_id)
            pid = connection.execute(playlist_query).first()
            if not pid:
                return "No playlist exists for the given playlist ID"

            #check if the song exists, return if it doesn't
            song_query = sqlalchemy.select(songs.c.id).where(songs.c.id == song_id)
            sid = connection.execute(song_query).first()
            if not sid:
                return "No song exists for the given song ID"

            #check if the song is already in the playlist, return if it is
            playlist_song_query = sqlalchemy.select(playlist_songs.c.song_id).where(playlist_songs.c.playlist_id == playlist_id)
            songs_in_playlist = connection.execute(playlist_song_query)
            for song in songs_in_playlist:
                if song.song_id == song_id:
                    return "Song is already in playlist"

            #add entry to playlist_songs
            insert_query = sqlalchemy.insert(playlist_songs).values(playlist_id=playlist_id, song_id=song_id)
            connection.execute(insert_query)
            return "Song added to playlist"
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

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
            rowcount = 0
            for row in result:
                rowcount += 1
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
            if rowcount == 0:
                return "No album exists for the given album ID"
            return "Added album to playlist"

    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

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
    try:
        with db.engine.begin() as connection:
            playlist_query = sqlalchemy.select(playlists.c.id, playlists.c.creator_id, playlists.c.title,
                                               playlists.c.mood).where(playlists.c.id == playlist_id)
            playlist = connection.execute(playlist_query).first()
            if not playlist:
                return "No playlist exists for the given playlist ID"
            song_query = sqlalchemy.select(songs.c.title, songs.c.genre, songs.c.duration).join(playlist_songs,
                                                                                                songs.c.id == playlist_songs.c.song_id).where(
                playlist_songs.c.playlist_id == playlist_id)
            songs_info = connection.execute(song_query)
            song_list = []
            for song in songs_info:
                song_list.append({
                    "title": song.title,
                    "genre": song.genre,
                    "duration_seconds": song.duration
                })
            return {
                "Name": playlist.title,
                "Songs": song_list
            }
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
