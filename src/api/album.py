from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.exc import DBAPIError
from src import database as db
from src.api.song import Genre, Feedback, song_exists

router = APIRouter(
    prefix="/albums",
    tags=["albums"],
    dependencies=[Depends(auth.get_api_key)],
)

# Use reflection to derive table schema.
metadata_obj = sqlalchemy.MetaData()
albums = sqlalchemy.Table("albums", metadata_obj, autoload_with=db.engine)
users = sqlalchemy.Table("users", metadata_obj, autoload_with=db.engine)

class NewAlbum(BaseModel):
    user_id: int
    name: str
    genre: Genre

@router.post("/new")
def create_album(new_album: NewAlbum):
    try:
        with db.engine.begin() as conn:
            exists_criteria = (
                select(users.c.id).
                where((users.c.id == new_album.user_id) & (users.c.user_type != 'listener')).
                exists()
            )
            artist_exists = conn.execute(select(users.c.id).where(exists_criteria)).scalar()

            if artist_exists:
                new_id = conn.execute(
                sqlalchemy.insert(albums).values(
                        artist_id=new_album.user_id,
                        title=new_album.name,
                        genre=new_album.genre, 
                ).returning(albums.c.id)).scalar_one()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="bad request: artist with the provided user_id does not exist"
                )
            return {"album_id": new_id}
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

def album_exists(album_id, connection):
    sql_to_execute = """SELECT * from albums WHERE id = :album_id"""
    exists = connection.execute(sqlalchemy.text(sql_to_execute),
                                [{"album_id": album_id}]).fetchone()
    if exists:
        return True
    else:
        return False

@router.post("/{album_id}/add-song/{song_id}")
def add_song_to_album(album_id: int, song_id: int):
    sql_to_execute = """UPDATE songs SET album_id = :album_id 
    WHERE id = :song_id"""
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
            SELECT songs.id, songs.title AS song_title, albums.title AS album_title
            FROM songs 
            JOIN albums ON album_id = albums.id
            WHERE songs.id = :id
            """), [{"id" : song_id}])
            if result.rowcount != 0:
                titles = result.first()
                connection.execute(sqlalchemy.text(sql_to_execute),
                [{"album_id": album_id, "song_id": song_id}])
                return titles.song_title + " added to " + titles.album_title
            
            return "Given song id does not exist." 
    
    except DBAPIError as error: 
        return f"Error returned: <<<{error}>>>"


@router.get("/{album_id}")
def get_songs_from_album(album_id: int):
    try:
        sql_to_execute = """
            SELECT songs.title, songs.genre, songs.duration 
            FROM songs
            WHERE album_id = :album_id
        """
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
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

@router.post("/{album_id}/rate")
def rate_album(album_id: int, feedback: Feedback):
    sql_to_execute = """INSERT INTO feedback (rating, feedback_type, user_id, album_id) VALUES (:r, :f, :u, :a)"""
    try:
        with db.engine.begin() as connection:
            if album_exists(album_id, connection):
                connection.execute(sqlalchemy.text(sql_to_execute),
                                            [{"r": feedback.rating, "f": feedback.feedback_category, "u":feedback.user, "a": album_id}])
                return "Thank you for your feedback"
            else:
                return "Given Album Id does not exist"
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

@router.get("/{album_id}/reviews")
def get_reviews_by_album(album_id: int):
    sql_to_execute = """SELECT COUNT(*) AS total_reviews, SUM(rating) AS total_rating FROM feedback WHERE album_id = :album_id"""
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql_to_execute),
                                        [{"album_id": album_id}]).first()
            if result.total_reviews == 0:
                return "No ratings exist for given album"
            avg_rating = "{:.2f}".format(result.total_rating / result.total_reviews)
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

    return {"avg_rating": avg_rating}