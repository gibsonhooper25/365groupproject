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
def create_curated_playlist():
    pass

class NewPlaylist(BaseModel):
    listener: bool #true if listener, false if artist - used for mapping to account name
    email: str
    password: str
    name: str
    mood: song.Mood

@router.post("/new/personal")
def create_personal_playlist(playlist_info: NewPlaylist):
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
        insert_query = sqlalchemy.insert(playlists).values(creator_id=user_id, title=playlist_info.name, mood=playlist_info.mood)
        connection.execute(insert_query)
    return "New empty playlist created"

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
def add_album_songs_to_playlist():
    pass

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
