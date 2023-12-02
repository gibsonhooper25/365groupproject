# Fake Data Modeling
spotify approximations: 
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

->
- 240 songs
- 1376 users
- 9582 playlists
- 958027 playlist_songs
- 1258 comments
- 25151 feedback ratings
- 240 mood_songs
- 4126 user_preferences

For a total of 1 million rows.

# Performance Results of Hitting Endpoints


# Performance Tuning