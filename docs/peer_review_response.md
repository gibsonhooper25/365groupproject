# Changes to Code
### Molly's Suggestions:
1. Changed Genre Enum and Mood to import from songs instead of re-defining it
2. Added password encryption using salt
3. Added comments to non-trivial functions
4. Converted most queries to strings
5. Added Try block to create_personal_playlist and get_songs_from_album
6. 
7. 
8. Changed add_album_songs_to_playlist to use album_exists boolean instead of rowcount
9. The two joins in get_all_songs and get_songs_from_album are necesarry to retreive the name of the album and the artist name rather than their ids. This may not be obvious because we renamed the colums in the query.
10. Playlists are identified by their unique id meaning that two curated playlists with the same name could be differentiated by their id.
11. Get songs now allows user to select a range of songs to return
12. Pydantic already checks that the feedback_catagory is an expected value but we added constraints on the ratings to be from 1 to 5 as we would expect

### Pau's Suggestions:
1. Added validation functions to check if a given song or album exists
2. Addressed above
3. 
4. Changed get_playlist to single query
5. fetchall not used
6. We've opted to return more descriptive messages so we have kept this logic in python while making it more readable
7. song.py returns a message in the event it cannot find a song
8. Added a seperate endpoint for assigning moods to songs
9. Addressed above
10. snake_case is used
11. Made seperate functions for checking albums and songs existence
12. Curated playlists are supposed to give a randomized selection of songs with the given mood so the randomization (ORDER BY RANDOM()) is necessary here

### Artin's Suggestions:
1. Added "supabase” directory to .gitignore
2. Added “.vscode” directory to .gitignore
3. The different use cases for the endpoints could allow us to seperate the spec for Listeners and Artists but we find it useful and intutitive to serperated based on the entity.
4. Addressed above
5. Changed to only query from mood_songs
6. The playlist will not be overwritten bacuase this is only an insert not an update. The user would then have access to both the original and new playlist with the same name and could differentiate the two by their id.
7. Addressed above
8. Addressed above
9. Addressed above
10. Addressed above
11. Switched all to lowercase
12. Addressed above

### Dillon's Suggestions:
1. Addressed above
2. Addressed above
3. Addressed above
4. Addressed above
5. Addressed above
6. Addressed above
7. Added descriptive returns telling user how they feedback was recorded
8. Adjusted to use only one query to insert moods
9. Addressed above
10. Addressed above
11. 
12. 
# Changes to Schema