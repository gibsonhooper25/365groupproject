from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.exc import DBAPIError
from src import database as db

router = APIRouter(
    prefix="/albums",
    tags=["albums"],
    dependencies=[Depends(auth.get_api_key)],
)

class Genre(str, Enum):
    jazz = "Jazz"
    blues = "Blues"
    rnb = "RnB"
    hip_hop = "Hip Hop"
    country = "Country"
    pop = "Pop"
    rock = "Rock"
    classical = "Classical"
    reggae = "Reggae"
    folk = "Folk"
    edm = "EDM"
    indie = "Indie"
    metal = "Metal"
    soundtrack = "Soundtrack"


# Use reflection to derive table schema.
metadata_obj = sqlalchemy.MetaData()
albums = sqlalchemy.Table("albums", metadata_obj, autoload_with=db.engine)
artists = sqlalchemy.Table("artists", metadata_obj, autoload_with=db.engine)

class NewAlbum(BaseModel):
    artist_id: int
    name: str
    genre: Genre

@router.post("/new")
def create_album(new_album: NewAlbum):
    try:
        with db.engine.begin() as conn:
            exists_criteria = (
                select(artists.c.id).
                where(artists.c.id == new_album.artist_id).
                exists()
            )
            artist_exists = conn.execute(select(artists.c.id).where(exists_criteria)).scalar()

            if artist_exists:
                new_id = conn.execute(
                sqlalchemy.insert(albums).values(
                        artist_id=new_album.artist_id,
                        title=new_album.name,
                        genre=new_album.genre, 
                ).returning(albums.c.id)).scalar_one()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="bad request: artist with the provided artist_id does not exist"
                )
            return {"album_id": new_id}
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


@router.post("/{album_id}/add-song/{song_id}")
def add_song_to_album(album_id: int, song_id: int):
    sql_to_execute = """INSERT INTO album_songs (album_id, song_id) VALUES
    (:album_id, :song_id)"""
    try:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql_to_execute),
            [{"album_id": album_id, "song_id": song_id}])
            return "ok"  
    except DBAPIError as error: 
        return f"Error returned: <<<{error}>>>"

    

@router.get("/{album_id}")
def get_songs_from_album(album_id: int):
    sql_to_execute = """SELECT songs.title, songs.genre, songs.duration 
    FROM album_songs
    JOIN albums ON albums.id = album_songs.album_id 
    JOIN songs ON songs.id = album_songs.song_id
    WHERE album_id = :album_id"""
    return_list = []
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute),
        [{"album_id": album_id}])

        for row in result:
            return_list.append({
                "title": row.title,
                "genre": row.genre,
                "duration": row.duration
            })

    return return_list