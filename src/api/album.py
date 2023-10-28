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
    rock = "Rock"
    jazz = "Jazz"
    pop = "Pop"
    hip_hop = "Hip Hop"
    dance = "Dance"
    electronic = "Electronic"
    disco = "Disco"
    classical = "Classical"
    blues = "Blues"
    heavy_metal = "Heavy Metal"
    country = "Country"
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