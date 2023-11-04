import sqlalchemy
from fastapi import APIRouter, Depends
from src.api import auth
from src import database as db
from sqlalchemy.exc import DBAPIError

router = APIRouter(
    prefix="/playlists",
    tags=["playlists"],
    dependencies=[Depends(auth.get_api_key)],
)

metadata_obj = sqlalchemy.MetaData()
playlists = sqlalchemy.Table("playlists", metadata_obj, autoload_with=db.engine)
playlist_songs = sqlalchemy.Table("playlist_songs", metadata_obj, autoload_with=db.engine)
songs = sqlalchemy.Table("songs", metadata_obj, autoload_with=db.engine)


@router.post("/new/curated")
def create_curated_playlist():
    pass

@router.post("/new/personal")
def create_personal_playlist():
    pass

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
