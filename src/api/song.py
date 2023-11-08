from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from enum import Enum


router = APIRouter(
    prefix="/songs",
    tags=["songs"],
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

class Mood(str, Enum):
    happy = "happy"
    sad = "sad"
    nostalgic = "nostalgic"
    relaxing = "relaxing"
    energetic = "energetic"
    angry = "angry"
    uplifting = "uplifting"
    calm = "calm"
    motivational = "motivational"
    experimental = "experimental"
    

class NewSong(BaseModel):
    title: str
    genre: Genre
    moods: list[Mood]
    duration: int

@router.get("/")
def get_all_songs():
    sql = """SELECT songs.title, songs.genre, duration, artists.name,
     albums.title AS album FROM songs
    JOIN artists ON artist_id = artists.id
    LEFT JOIN albums ON album_id = albums.id"""
    return_list = []
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql))
            for row in result:
                return_list.append({
                    "Title": row.title,
                    "Artist": row.name,
                    "Album": row.album,
                    "Genre": row.genre,
                    "Duration":row.duration,

                })

    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"
    return return_list

@router.post("/new")
def create_new_song(album_id: int, artist_id: int, song: NewSong):
    sql_to_execute = """INSERT INTO songs (title, genre, duration, album_id, artist_id)
    VALUES (:title, :genre, :duration, :album_id, :artist_id) RETURNING id"""
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql_to_execute), 
                [{"title": song.title, "genre": song.genre, "duration": song.duration,
                  "album_id": album_id, "artist_id": artist_id}])
            id = result.first().id

            for mood in song.moods:
                sql_to_execute = """INSERT INTO mood_songs (mood, song)
                VALUES (:mood, :song)"""
                connection.execute(sqlalchemy.text(sql_to_execute), 
                    [{"mood": mood.value, "song": id}])

    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

    return {"song_id": id}


class SongFeedbackType(str, Enum):
    quality = "sound quality"
    lyrics = "lyrics"
    vocals = "vocals"
    melody = "melody"
    originality = "originality"
    overall = "overall"

class SongFeedback(BaseModel):
    rating: int
    feedback_category: SongFeedbackType
@router.post("/{song_id}/rate")
def rate_song(song_id: int, feedback: SongFeedback):
    sql = """INSERT INTO feedback (rating, feedback_type, song_id) VALUES (:r, :f, :s)"""
    try:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql),
                                        [{"r": feedback.rating, "f": feedback.feedback_category, "s": song_id}])
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

    return "Thank you for your feedback"

@router.get("/{song_id}/reviews")
def get_reviews_by_song(song_id: int):
    sql = """SELECT COUNT(*) AS total_reviews, SUM(rating) AS total_rating FROM feedback WHERE song_id = :song_id"""
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql),
                                        [{"song_id": song_id}]).first()
            if result.total_reviews == 0:
                return "No ratings exist for given song"
            avg_rating = "{:.2f}".format(result.total_rating / result.total_reviews)
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

    return {"avg_rating": avg_rating}
