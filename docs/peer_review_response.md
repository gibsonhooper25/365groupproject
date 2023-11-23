# Changes to Code
Molly's Suggestions:
1. Changed Genre Enum and Mood to import from songs instead of re-defining it
2. Added password encryption using salt
3. 
4. 
5. Added Try block to create_personal_playlist and get_songs_from_album
6. 
7. 
8. Changed add_album_songs_to_playlist to use album_exists boolean instead of rowcount
9. The two joins in get_all_songs and get_songs_from_album are necesarry to retreive the name of the album and the artist name rather than their ids. This may not be obvious because we renamed the colums in the query.
10. Playlists are identified by their unique id meaning that two curated playlists with the same name could be differentiated by their id.
11. 
12. Pydantic already checks that the feedback_catagory is an expected value but we added constraints on the ratings to be from 1 to 5 as we would expect
Pau's Suggestions:
1. Added validation functions to check if a given song or album exists
2. Addressed above
3. 
4. Changed get_playlist to single query
5. 
6. 
7. 
8. 
9. 
10. 
11. 
12. Curated playlists are supposed to give a randomized selection of songs with the given mood so the randomization is necessary here
Artin's Suggestions:
1. 
2. 
3. 
4. 
5. Changed to only query from mood_songs
6. The playlist will not be overwritten bacuase this is only an insert not an update. The user would then have access to both the original and new playlist with the same name and could differentiate the two by their id.
7. 
8. 
9. 
10. 
11. 
12. 
Dillon's Suggestions:
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
9. 
10. Addressed above
11. 
12. 
# Changes to Schema