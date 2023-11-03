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
    relazing = "relaxing"
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


@router.post("/new")
def create_new_song(artist_ids: list[int], song: NewSong):
    sql_to_execute = """INSERT INTO songs (title, genre, duration)
    VALUES (:title, :genre, :duration) RETURNING id"""
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql_to_execute), 
                [{"title": song.title, "genre": song.genre, "duration": song.duration}])
            id = result.first().id

            for mood in song.moods:
                sql_to_execute = """INSERT INTO mood_songs (mood, song)
                VALUES (:mood, :song)"""
                connection.execute(sqlalchemy.text(sql_to_execute), 
                    [{"mood": mood.value, "song": id}])

            #in case of multiple artists
            for artist_id in artist_ids:
                sql_to_execute = """INSERT INTO artist_songs (artist_id, song_id)
                VALUES (:artist_id, :song_id)"""
                connection.execute(sqlalchemy.text(sql_to_execute), 
                    [{"artist_id": artist_id, "song_id": id}])
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

    return {"song_id": id}


