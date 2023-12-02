from fastapi import APIRouter, Depends
from pydantic import BaseModel, confloat
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from enum import Enum
from datetime import date


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
    release_date: date

class ContentType(str, Enum):
    album = "album",
    song = "song"

#returns list of all songs. Pagination works given lower bound and upper bound of songs which are sorted in order of title
@router.get("/")
def get_all_songs(lower_bound: int, upper_bound: int):
    sql = """SELECT songs.id, songs.title, songs.genre, duration, songs.release_date, users.name,
     albums.title AS album FROM songs
    JOIN users ON songs.artist_id = users.id
    LEFT JOIN albums ON album_id = albums.id
    ORDER BY songs.title ASC"""
    if upper_bound < lower_bound:
        return "Invalid lower and upper bound."
    return_list = []
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql))
            for row in result:
                return_list.append({
                    "title": row.title,
                    "artist": row.name,
                    "album": row.album,
                    "genre": row.genre,
                    "duration":row.duration,
                    "release_date": row.release_date
                })
        if lower_bound > len(return_list):
            return "End of song list reached."
        if upper_bound > len(return_list):
            upper_bound = len(return_list)
        if lower_bound < 0:
            lower_bound = 0

    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"
    return return_list[lower_bound:upper_bound]

@router.get("/{song_id}")
def get_song(song_id: int):
    sql_to_execute = """
        SELECT songs.title as song, songs.genre, songs.duration, songs.release_date, albums.title as album, users.name as artist
        FROM songs
        JOIN users ON users.id = songs.artist_id
        LEFT JOIN albums ON albums.id = songs.album_id 
        WHERE songs.id = :song_id
    """
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql_to_execute),
            [{"song_id": song_id}])
            song = result.first()
            if not song:
                return "Song with given id does not exist"
            return {
                "song": song.song,
                "genre": song.genre,
                "duration": song.duration,
                "album": song.album,
                "artist": song.artist,
                "release_date": song.release_date
            }
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

@router.post("/new")
def create_new_song(artist_id: int, song: NewSong):
    sql_to_execute = """INSERT INTO songs (title, genre, duration, artist_id, release_date)
    VALUES (:title, :genre, :duration, :artist_id, :release_date) RETURNING id"""
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql_to_execute), 
                [{"title": song.title, "genre": song.genre, "duration": song.duration,
                    "artist_id": artist_id, "release_date": song.release_date}])
            id = result.first().id

            mood_data = []
            for mood in song.moods:
                mood_data.append({"mood": mood.value, "song": id})
            sql_to_execute = """
                INSERT INTO mood_songs (mood, song)
                VALUES (:mood, :song)"""
            connection.execute(sqlalchemy.text(sql_to_execute), mood_data)

    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

    return {"song_id": id}

#associates enumerated mood with an existing song. Shows error message if song does not exist
@router.post("/new/{song_id}/moods")
def add_mood_to_song(song_id: int, mood: Mood):
    try:
        with db.engine.begin() as connection:
            sql_to_execute = """
                INSERT INTO mood_songs (mood, song)
                VALUES (:mood, :song)"""
            title = song_title(song_id, connection)
            if title:
                connection.execute(sqlalchemy.text(sql_to_execute),
                    [{"mood": mood, "song": song_id}])
                return "Mood: "+ mood + " added to " + title
            return "Song with given song id does not exist"
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"
 
    

class FeedbackType(str, Enum):
    quality = "sound quality"
    lyrics = "lyrics"
    vocals = "vocals"
    melody = "melody"
    originality = "originality"
    overall = "overall"

class Feedback(BaseModel):
    rating: confloat(ge=1.0, le=5.0)
    feedback_category: FeedbackType
    user: int

#helper function to determine if song with given song_id exists
def song_title(song_id, connection):
    sql_to_execute = """SELECT * from songs WHERE id = :song_id"""
    song = connection.execute(sqlalchemy.text(sql_to_execute),
                                [{"song_id": song_id}]).fetchone()
    if song:
        return song.title
    else:
        return False

#associates feedback information with a given song. Error if song does not exist
@router.post("/{song_id}/rate")
def rate_song(song_id: int, feedback: Feedback):
    sql = """INSERT INTO feedback (rating, feedback_type, user_id, song_id) VALUES (:r, :f, :u, :s)"""
    try:
        with db.engine.begin() as connection:
            song = song_title(song_id, connection)
            if song:
                connection.execute(sqlalchemy.text(sql),
                                            [{"r": feedback.rating, "f": feedback.feedback_category, "u":feedback.user, "s": song_id}])
                return "You gave '" + song + "' a " + str(feedback.rating) + \
                " for category: " + feedback.feedback_category + ". Thank you for your feedback"
            else:
                return "Given Song Id does not exist"
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

#returns the average feedback rating for a given song, if the song exists and has ratings
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
