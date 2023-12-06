from fastapi import APIRouter, Depends
from pydantic import BaseModel, conint
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from enum import Enum
from src.api.song import Genre, Mood

router = APIRouter(
    prefix="/discovery",
    tags=["discovery"],
    dependencies=[Depends(auth.get_api_key)],
)

class Preference(BaseModel):
    user_id: int
    update_type: str
    update:str

class PreferenceType(str, Enum):
    genre = "genre"
    mood = "mood"
   
#only called if their preferences have not been set yet
#will see what they have in their playlists and fill out preference table for
#them if they are not in user_preferences already
@router.post("/{user_id}")
def preference_defaults(user_id: int):
    try:
        with db.engine.begin() as connection:
            #check to see if user already has preferences set
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE id = :user_id
                """
            ), [{"user_id": user_id}])
            if result.rowcount == 0:
                return "Given user id does not exist."
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM user_preferences
                WHERE user_id = :user_id
                """
            ), [{"user_id": user_id}])
            if result.rowcount != 0:
                return "User preferences already set."

            #creating default moods
            top_moods = connection.execute(sqlalchemy.text(
            """
                SELECT mood_songs.mood AS mood
                FROM playlists 
                JOIN playlist_songs ON playlist_id = playlists.id
                JOIN songs ON song_id = songs.id
                JOIN mood_songs ON song = songs.id
                WHERE creator_id = :user_id
                GROUP BY mood_songs.mood
                ORDER BY COUNT(*) DESC
                LIMIT 2
            """
            ), [{"user_id": user_id}]) 
            if top_moods.rowcount == 0:
                return "Insufficient data for discovery, please add preferences manually or create a playlist."
            for mood in top_moods:
                quick_insert(Preference(user_id = user_id, update_type = "mood", update = mood.mood), connection)
                if result == "Invalid preference":
                    return "Invalid preference type."

            #creating default genres
            top_genres = connection.execute(sqlalchemy.text(
                """
                SELECT genre
                FROM playlists 
                JOIN playlist_songs ON playlist_id = playlists.id
                JOIN songs ON song_id = songs.id
                WHERE creator_id = :user_id
                GROUP BY genre
                ORDER BY COUNT(*) DESC
                LIMIT 2
                """
            ), [{"user_id": user_id}]) 
            if top_genres.rowcount == 0:
                return "Insufficient data for discovery, please add preferences manually or create a playlist."
            for genre in top_genres:
                result = quick_insert(Preference(user_id = user_id, update_type = "genre", update =genre.genre), connection)
                if result == "Invalid preference":
                    return "Invalid preference type."
            
            return "Preferences successfully set."
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

#no checks, which is fine for preference_defaults
def quick_insert(update: Preference, connection):
    connection.execute(sqlalchemy.text(
        """
        INSERT INTO user_preferences (user_id, preference_type, preference)
        VALUES (:user_id, :update_type, :update)
        """
        ), [{"user_id": update.user_id, "update_type": update.update_type, 
        "update": update.update}])
    return "ok"

@router.get("/preferences/{user_id}")
def get_preferences(user_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE id = :user_id
                """
            ), [{"user_id": user_id}])
            if result.rowcount == 0:
                return "Given user id does not exist."
            result = connection.execute(sqlalchemy.text(
                """
                SELECT preference_type, preference FROM user_preferences
                WHERE user_id = :user_id 
                """
            ),[{"user_id": user_id}])
            genres = []
            moods = []
            for row in result:
                if row.preference_type == "genre":
                    genres.append(row.preference)
                elif row.preference_type == "mood":
                    moods.append(row.preference)
            if len(genres) == 0 and len(moods) == 0:
                return "No preferences set."
        return {"genres": genres, "moods": moods}
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"


#add a user preference, can be either a preferred genre, mood, or artist
@router.post("/preferences/{user_id}")
def add_preference(update: Preference):
    
    if update.update_type != "genre" and update.update_type != "mood":
        return "Invalid preference"
    if update.update_type == "mood" and update.update not in [mood for mood in Mood]:
        return "Invalid mood"
    if update.update_type == "genre" and update.update not in [genre for genre in Genre]:
        return "Invalid genre"
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM user_preferences
                WHERE user_id = :user_id AND preference_type = :update_type AND
                preference = :update
                """
            ),[{"user_id": update.user_id, "update_type": update.update_type, 
                "update": update.update}])
            if result.rowcount != 0:
                return "Preference already exists"
            
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO user_preferences (user_id, preference_type, preference)
                VALUES (:user_id, :update_type, :update)
                """
            ), [{"user_id": update.user_id, "update_type": update.update_type, 
                "update": update.update}])
        return "Preference updated"
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

#deletes either a genre, mood from the preference list
@router.delete("/preferences/{user_id}")
def delete_preference(deletion: Preference):
    if deletion.update_type != "genre" and deletion.update_type != "mood":
        return "Invalid preference"
    if deletion.update_type == "mood" and deletion.update not in [mood for mood in Mood]:
        return "Invalid mood"
    if deletion.update_type == "genre" and deletion.update not in [genre for genre in Genre]:
        return "Invalid genre"
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM user_preferences
                WHERE user_id = :user_id AND preference_type = :update_type AND
                preference = :update
                """
            ),[{"user_id": deletion.user_id, "update_type": deletion.update_type, 
                "update": deletion.update}])
            if result.rowcount == 0:
                return "Preference does not exist"
            
            connection.execute(sqlalchemy.text(
                """
                DELETE FROM user_preferences 
                WHERE
                user_id = :user_id AND preference_type = :update_type AND preference = :update
                """
            ), [{"user_id": deletion.user_id, "update_type": deletion.update_type, 
                "update": deletion.update}])
        return "Preference updated"
    
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

@router.get("/new_releases/{user_id}")
def get_new_releases(user_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE id = :user_id
                """
            ), [{"user_id": user_id}])
            if result.rowcount == 0:
                return "Given user id does not exist."
            
            preferences = connection.execute(sqlalchemy.text(
                """
                SELECT preference_type, preference FROM user_preferences
                WHERE user_id = :user_id
                """
            ),[{"user_id": user_id}]) 

            #if user does not have any registered preferences, they are added
            #automatically
            if preferences.rowcount == 0:
                result = preference_defaults(user_id)
                if result != "Preferences successfully set.":
                    return result


            #get new songs whose mood and genre matches user preferences
            genres = []
            moods = []

            for preference in preferences:
                if preference.preference_type == "genre":
                    genres.append(preference.preference)
                elif preference.preference_type == "mood":
                    moods.append(preference.preference)
            
            #if no preferred genres, then it should be open to all
            if len(genres) == 0:
                [genres.append(genre) for genre in Genre]
            #if no preferred moods, then it should be open to all
            if len(moods) == 0:
                [moods.append(mood) for mood in Mood]

            #finds songs that match users preferred genres and moods
            #ignores songs that are already in users playlists
            #then orders it by how recently it was released,
            #returns 20 if 20 exist
            matched_songs = connection.execute(sqlalchemy.text(
                """
                WITH user_songs AS 
                (
                    SELECT song_id FROM playlists
                    JOIN playlist_songs ON playlist_id = playlists.id
                    WHERE creator_id = :user_id
                )
                SELECT DISTINCT songs.created_at, title, name, genre, duration, release_date
                FROM songs
                JOIN mood_songs ON song = songs.id
                JOIN users ON artist_id = users.id
                LEFT JOIN user_songs ON user_songs.song_id = songs.id
                WHERE genre::text = ANY(:genres) AND mood::text = ANY(:moods) AND
                user_songs.song_id IS NULL
                ORDER BY songs.created_at DESC
                LIMIT 20
                """
            ), [{"user_id": user_id, "genres" : genres, "moods" : moods}])   
            
            return_list = []
            if matched_songs.rowcount != 0:
                return_list.append("Songs you might enjoy based on current preferences")
            for song in matched_songs:
                return_list.append({
                    "title": song.title,
                    "artist": song.name,
                    "genre": song.genre,
                    "duration": song.duration,
                    "release_date": song.release_date
                })
            
            #finds new artists, if their songs match the preferred genre and are not
            #already known to the user, it will return 5 recently added artists.
            new_artists = connection.execute(sqlalchemy.text(
                """
                WITH user_artists AS 
                (
                    SELECT DISTINCT artist_id FROM playlists
                    JOIN playlist_songs ON playlist_id = playlists.id
                    JOIN songs ON songs.id = song_id
                    WHERE creator_id = :user_id
                )
                SELECT DISTINCT users.created_at, name FROM songs
                LEFT JOIN user_artists ON user_artists.artist_id = songs.artist_id
                JOIN users ON songs.artist_id = users.id
                WHERE user_artists.artist_id IS NULL AND genre::text = ANY(:genres)
                ORDER BY users.created_at DESC
                LIMIT 5
                """
            ), [{"user_id": user_id, "genres" : genres}]) 
            if new_artists.rowcount != 0: 
                return_list.append("Some new artists you might enjoy")
            for artist in new_artists:
                return_list.append(artist.name)

            #gets new releases from artists the user prefers/follows, meaning they
            #have more than three songs of that artist on a playlist
            new_releases = connection.execute(sqlalchemy.text(
                """
                WITH followed_artists AS 
                (
                    SELECT DISTINCT artist_id FROM playlists
                    JOIN playlist_songs ON playlist_id = playlists.id
                    JOIN songs ON songs.id = song_id
                    WHERE creator_id = :user_id
                    GROUP BY artist_id
                    HAVING COUNT(DISTINCT song_id) > 3
                ),
                user_songs AS(
                    SELECT song_id FROM playlists
                    JOIN playlist_songs ON playlist_id = playlists.id
                    WHERE creator_id = :user_id
                )
                SELECT songs.created_at, title, name, genre, duration, release_date
                FROM songs
                JOIN users ON artist_id = users.id
                LEFT JOIN followed_artists ON followed_artists.artist_id = songs.artist_id
                LEFT JOIN user_songs ON user_songs.song_id = songs.id
                WHERE followed_artists.artist_id IS NOT NULL AND user_songs.song_id IS NULL
                ORDER BY songs.created_at DESC
                LIMIT 10
                """
            ), [{"user_id": user_id}])   
            if new_releases.rowcount != 0: 
                return_list.append("New releases from artists you love")
            for song in new_releases:
                return_list.append({
                    "title": song.title,
                    "artist": song.name,
                    "genre": song.genre,
                    "duration": song.duration,
                    "release_date": song.release_date
                })
        return return_list
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"

@router.patch("/spotlight/add")
def add_artist_to_spotlight(user_id: int, description: str):
    try:
        with db.engine.begin() as connection:
            #check to make sure the user that is being spotlighted is an artist
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE id = :user_id AND (user_type = 'artist' OR user_type = 'listener_and_artist')
                """
            ),[{"user_id": user_id}])
            if result.rowcount == 0:
                return "No artist exists for given user id"
            
            connection.execute(sqlalchemy.text(
                """
                UPDATE users
                SET spotlight = True, description = :description
                WHERE id = :user_id
                """
            ), [{"user_id": user_id, "description": description}])

        return "Spotlight given to user: " + str(user_id)
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"
    
@router.patch("/spotlight")
def remove_artist_from_spotlight(user_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE id = :user_id AND spotlight = TRUE
                """
            ), [{"user_id": user_id}])
            if result.rowcount == 0:
                return "No spotlighted artist for the given id."
            connection.execute(sqlalchemy.text(
                """
                UPDATE users
                SET spotlight = False
                WHERE id = :user_id
                """
            ),[{"user_id": user_id}])

        return "Spotlight removed from user: " + str(user_id)
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"
    
#returns a list of songs from spotlighted artists that match the users preferred genre 
#preferences
#if no preferences are set, it returns any songs from spotlighted artists
@router.get("/spotlight/{user_id}")
def get_spotlight_list(user_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE id = :user_id
                """
            ), [{"user_id": user_id}])
            if result.rowcount == 0:
                return "Given user id does not exist."
            result = connection.execute(sqlalchemy.text(
                """
                SELECT preference FROM user_preferences
                WHERE user_id = :user_id AND preference_type = 'genre'
                """
            ), [{"user_id": user_id}])
            genres = []
            for row in result:
                genres.append(row.preference)
            
            if len(genres) == 0:
                [genres.append(genre) for genre in Genre]
        
            result = connection.execute(sqlalchemy.text(
                """
                WITH user_songs AS(
                    SELECT song_id FROM playlists
                    JOIN playlist_songs ON playlist_id = playlists.id
                    WHERE creator_id = :user_id
                )
                SELECT title, name, genre, duration, release_date
                FROM users
                JOIN songs ON users.id = artist_id
                LEFT JOIN user_songs ON user_songs.song_id = songs.id
                WHERE (users.user_type = 'artist' OR users.user_type = 'listener_and_artist')
                AND spotlight = TRUE AND genre::text = ANY(:genres) AND user_songs.song_id IS NULL
                ORDER BY RANDOM()
                LIMIT 15
                """
            ), [{"user_id": user_id, "genres": genres}])

        return_list = []
        for row in result: 
            return_list.append({
                "title": row.title,
                "artist": row.name,
                "genre": row.genre,
                "duration": row.duration,
                "release_date": row.release_date
            })

        return return_list
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"