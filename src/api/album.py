from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.exc import DBAPIError
from src import database as db
from src.api.song import Genre, Feedback, song_title
from datetime import date

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
    release_date: date

#creates empty album with a given name, genre, and release date. user submitting request must be either artist or listener_and_artist
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
                        release_date=new_album.release_date
                ).returning(albums.c.id)).scalar_one()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="bad request: artist with the provided user_id does not exist"
                )
            return {"album_id": new_id}
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

#returns album title of a given album id, used to verify that album exists
def album_title(album_id, connection):
    sql_to_execute = """SELECT title from albums WHERE id = :album_id"""
    album = connection.execute(sqlalchemy.text(sql_to_execute),
                                [{"album_id": album_id}]).fetchone()
    if album:
        return album.title
    else:
        return False

#adds song with given song id to album with given album_id. fails if either id does not correspond to an existing record
@router.post("/{album_id}/add-song/{song_id}")
def add_song_to_album(album_id: int, song_id: int):
    sql_to_execute = """UPDATE songs SET album_id = :album_id 
    WHERE id = :song_id"""
    try:
        with db.engine.begin() as connection:
            # Check to see if album exists
            album = album_title(album_id, connection)
            if not album:
                return "Given album id does not exist."
            # Check to see if song exists
            song = song_title(song_id, connection)
            if song:
                connection.execute(sqlalchemy.text(sql_to_execute),
                [{"album_id": album_id, "song_id": song_id}])
                return "Added '" + song + "' to '" + album + "'"
            return "Given song id does not exist." 
    
    except DBAPIError as error: 
        return f"Error returned: <<<{error}>>>"

@router.delete("/{album_id}/songs/{song_id}")
def remove_song_from_album(song_id: int):
    sql_to_execute = """UPDATE songs SET album_id = NULL
    WHERE id = :song_id"""
    try:
        with db.engine.begin() as connection:
            #Get current album
            result = connection.execute(sqlalchemy.text("""
                SELECT album_id FROM songs WHERE id = :song_id
            """),[{"song_id": song_id}])

            song = song_title(song_id, connection)
            # Check to see if song exists
            if song:
                album_id = result.first().album_id
                if not album_id:
                    return "'"+ song + "' not attached to any album."
                
                album = album_title(album_id, connection)
                connection.execute(sqlalchemy.text(sql_to_execute),
                [{"song_id": song_id}])
                return "Removed '" + song + "' from '" + album + "'"
            return "Given song id does not exist." 
    
    except DBAPIError as error: 
        return f"Error returned: <<<{error}>>>"

#returns list of songs on the album with given album id. returns empty list if album is empty, returns error message if album does not exist
@router.get("/{album_id}")
def get_songs_from_album(album_id: int):
    try:
        sql_to_execute = """
            SELECT songs.title, songs.genre, songs.duration, songs.release_date
            FROM songs
            WHERE album_id = :album_id
        """
        return_list = []
        with db.engine.begin() as connection:
            if album_title(album_id, connection):
                result = connection.execute(sqlalchemy.text(sql_to_execute),
                [{"album_id": album_id}])

                for row in result:
                    return_list.append({
                        "title": row.title,
                        "genre": row.genre,
                        "duration": row.duration,
                        "release_date": row.release_date
                    })
            else:
                return "Album with given album_id does not exist"

        return return_list
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

#submit feedback for a given album. See Feedback class for information on feedback. Returns error message if album does not exist, otherwise returns success message
@router.post("/{album_id}/rate")
def rate_album(album_id: int, feedback: Feedback):
    sql_to_execute = """INSERT INTO feedback (rating, feedback_type, user_id, album_id) VALUES (:r, :f, :u, :a)"""
    try:
        with db.engine.begin() as connection:
            album = album_title(album_id, connection)
            if album:
                connection.execute(sqlalchemy.text(sql_to_execute),
                [{"r": feedback.rating, "f": feedback.feedback_category, "u":feedback.user, "a": album_id}])
                
                return "You gave '" + album + "' a " + str(feedback.rating) + \
                " for category: " + feedback.feedback_category + ". Thank you for your feedback"
            else:
                return "Given Album Id does not exist"
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

#Returns the average rating for an album from the feedback it received from rate_album(). Returns error message if album has no ratings.
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