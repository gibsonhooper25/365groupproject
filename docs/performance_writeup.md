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
## Songs
- Get all songs - `/songs/` - {time to execute in ms}
- Get song - `/songs/{song_id}`- {time to execute in ms}
- Create new song - `/songs/new` - {time to execute in ms}
- Add mood to song - `/songs/new/{song_id}/moods` - {time to execute in ms}
- Rate song - `/songs/{song_id}/rate` - {time to execute in ms}
- Get reviews for song - `/songs/{song_id}/reviews` - {time to execute in ms}
## Albums
- create new album - `/albums/new` - {time to execute in ms}
- add song to album - `/albums/{album_id}/add-song/{song_id}` - {time to execute in ms}
- remove song from album - `/albums/{album_id}/songs/{song_id}` - {time to execute in ms}
- get songs from album - `/albums/{album_id}` - {time to execute in ms}
- rate album - `/albums/{album_id}/rate` - {time to execute in ms}
- get reviews by album - `/albums/{album_id}/reviews` - {time to execute in ms}
## Playlists
- create curated playlist - `/playlists/new/curated` - {time to execute in ms}
- create curated playlist advanced - `/playlists/new/advanced` - {time to execute in ms}
- create personal playlist - `/playlists/new/personal` - {time to execute in ms}
- add song to playlist - `/playlists/{playlist_id}/add-song/{song_id}` - {time to execute in ms}
- add album songs to playlist - `/playlists/{playlist_id}/add-songs/{album_id}` - {time to execute in ms}
- delete song from playlist - `/playlists/{playlist_id}/remove-song/{song_id}` - {time to execute in ms}
- get playlist - `/playlists/{playlist_id}` - {time to execute in ms}

## Users
- add user - `/users/` - {time to execute in ms}
- login - `/users/login` - {time to execute in ms}

## Discovery
- preference defaults - `/discovery/{user_id}` - {time to execute in ms}
- get preferences - `/discovery/preferences/{user_id}` - {time to execute in ms}
- add preference - `/discovery/preferences/{user_id}` - {time to execute in ms}
- delete preferences - `/discovery/preferences/{user_id}` - {time to execute in ms}
- get new releases - `/discovery/new_releases/{user_id}` - {time to execute in ms}
- add artist to spotlight - `/discovery/spotlight/add` - {time to execute in ms}
- remove artist from spotlight - `/discovery/spotlight` - {time to execute in ms}
- get spotlight list - `/discovery/spotlight/{user_id}` - {time to execute in ms}

## Three Slowest Endpoints
- a
- b
- c

# Performance Tuning

- [endpoint 1]
  - [results of explain]
  - [what index to add]
  - [command for adding index]
  - [results of new explain]
  - [did it improve enough]

- [endpoint 2]
  - [results of explain]
  - [what index to add]
  - [command for adding index]
  - [results of new explain]
  - [did it improve enough]

- [endpoint 3]
  - [results of explain]
  - [what index to add]
  - [command for adding index]
  - [results of new explain]
  - [did it improve enough]