# Fake Data Modeling

The data is populated using the code in src/populate_tables.py. To calculate the rows per table we used the following:

Spotify approximations: 
- 100 million songs
- 574 million users
- 4 billion playlists
- around 100 songs per playlist -> 400 billion playlist_songs
- 5 million albums

our data approximations:
- average of 5 comments per song and album -> 525 million comments
- average of 100 feedback ratings per song and album -> 10.5 billion feedback ratings
- 20 moods, average 1 mood per song -> 100 million mood_songs
- average 3 user preferences per user -> 1.722 billion user_preferences

total rows from above data: 417,526,000,000

-> multiplier = 1,000,000 / 417,526,000,000 = 0.000002395060427

Multiplying the above multiplier by each of the row values gives the final row counts for each table:
- 240 songs
- 1375 users
- 9580 playlists
- 958024 playlist_songs
- 12 albums
- 1257 comments
- 25148 feedback ratings
- 240 mood_songs
- 4124 user_preferences

For a total of 1 million rows.

# Performance Results of Hitting Endpoints


# Performance Tuning