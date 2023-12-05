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
- Get all songs - `/songs/` - 79 ms
- Get song - `/songs/{song_id}`- 12 ms
- Create new song - `/songs/new` - 19 ms
- Add mood to song - `/songs/new/{song_id}/moods` - 82 ms
- Rate song - `/songs/{song_id}/rate` - 9 ms
- Get reviews for song - `/songs/{song_id}/reviews` - 14 ms
## Albums
- create new album - `/albums/new` - 78 ms
- add song to album - `/albums/{album_id}/add-song/{song_id}` - 22 ms
- remove song from album - `/albums/{album_id}/songs/{song_id}` - 9 ms
- get songs from album - `/albums/{album_id}` - 11 ms
- rate album - `/albums/{album_id}/rate` - 13 ms
- get reviews by album - `/albums/{album_id}/reviews` - 14 ms
## Playlists
- create curated playlist - `/playlists/new/curated` - 82 ms
- create curated playlist advanced - `/playlists/new/advanced` - 59 ms
- create personal playlist - `/playlists/new/personal` - 61 ms
- add song to playlist - `/playlists/{playlist_id}/add-song/{song_id}` - 6 ms
- add album songs to playlist - `/playlists/{playlist_id}/add-songs/{album_id}` - 155 ms
- delete song from playlist - `/playlists/{playlist_id}/remove-song/{song_id}` - 66 ms
- get playlist - `/playlists/{playlist_id}` - 40 ms

## Users
- add user - `/users/` - 68 ms
- login - `/users/login` - 10 ms

## Discovery
- preference defaults - `/discovery/{user_id}` - 96 ms
- get preferences - `/discovery/preferences/{user_id}` - 18 ms
- add preference - `/discovery/preferences/{user_id}` - 14 ms
- delete preferences - `/discovery/preferences/{user_id}` - 5 ms
- get new releases - `/discovery/new_releases/{user_id}` - 5236 ms
- add artist to spotlight - `/discovery/spotlight/add` - 12 ms
- remove artist from spotlight - `/discovery/spotlight` - 8 ms
- get spotlight list - `/discovery/spotlight/{user_id}` - 406 ms

## Three Slowest Endpoints
- get new releases
- get spotlight list
- add album to playlist

# Performance Tuning

- get new releases
  - In get new releases, there are multiple queries, but this is explain analyze on the one that takes the longest to run.
  ```
    | QUERY PLAN                                                                                                                                                                                                   |
  |
  | Limit  (cost=26930.04..26930.05 rows=1 width=50) (actual time=19833.238..19833.383 rows=0 loops=1)                                                                                                             |
  |   ->  Sort  (cost=26930.04..26930.05 rows=1 width=50) (actual time=19833.237..19833.382 rows=0 loops=1)                                                                                                        |
  |         Sort Key: songs.created_at DESC                                                                                                                                                                        |
  |         Sort Method: quicksort  Memory: 25kB                                                                                                                                                                   |
  |         ->  Nested Loop  (cost=26727.40..26930.03 rows=1 width=50) (actual time=19833.223..19833.368 rows=0 loops=1)                                                                                           |
  |               Join Filter: (users.id = songs.artist_id)                                                                                                                                                        |
  |               ->  Hash Anti Join  (cost=13401.45..13408.05 rows=1 width=44) (actual time=4.024..4.680 rows=241 loops=1)                                                                                        |
  |                     Hash Cond: (songs.id = playlist_songs.song_id)                                                                                                                                             |
  |                     ->  Seq Scan on songs  (cost=0.00..5.40 rows=240 width=52) (actual time=0.003..0.203 rows=241 loops=1)                                                                                     |
  |                     ->  Hash  (cost=13390.20..13390.20 rows=900 width=8) (actual time=4.006..4.117 rows=0 loops=1)                                                                                             |
  |                           Buckets: 1024  Batches: 1  Memory Usage: 8kB                                                                                                                                         |
  |                           ->  Gather  (cost=1214.92..13390.20 rows=900 width=8) (actual time=4.006..4.116 rows=0 loops=1)                                                                                      |
  |                                 Workers Planned: 2                                                                                                                                                             |
  |                                 Workers Launched: 2                                                                                                                                                            |
  |                                 ->  Hash Join  (cost=214.93..12300.20 rows=375 width=8) (actual time=0.485..0.486 rows=0 loops=3)                                                                              |
  |                                       Hash Cond: (playlist_songs.playlist_id = playlists.id)                                                                                                                   |
  |                                       ->  Parallel Seq Scan on playlist_songs  (cost=0.00..11036.93 rows=399193 width=16) (actual time=0.011..0.012 rows=1 loops=3)                                            |
  |                                       ->  Hash  (cost=214.81..214.81 rows=9 width=8) (actual time=0.432..0.432 rows=0 loops=3)                                                                                 |
  |                                             Buckets: 1024  Batches: 1  Memory Usage: 8kB                                                                                                                       |
  |                                             ->  Seq Scan on playlists  (cost=0.00..214.81 rows=9 width=8) (actual time=0.432..0.432 rows=0 loops=3)                                                            |
  |                                                   Filter: (creator_id = 2)                                                                                                                                     |
  |                                                   Rows Removed by Filter: 9585                                                                                                                                 |
  |               ->  Merge Join  (cost=13325.94..13521.21 rows=62 width=30) (actual time=82.269..82.269 rows=0 loops=241)                                                                                         |
  |                     Merge Cond: (users.id = songs_1.artist_id)                                                                                                                                                 |
  |                     ->  Index Scan using users_pkey1 on users  (cost=0.28..78.92 rows=1376 width=22) (actual time=0.007..0.007 rows=1 loops=241)                                                               |
  |                     ->  Unique  (cost=13325.67..13437.45 rows=62 width=8) (actual time=82.261..82.261 rows=0 loops=241)                                                                                        |
  |                           ->  GroupAggregate  (cost=13325.67..13437.30 rows=62 width=8) (actual time=82.260..82.260 rows=0 loops=241)                                                                          |
  |                                 Group Key: songs_1.artist_id                                                                                                                                                   |
  |                                 Filter: (count(DISTINCT playlist_songs_1.song_id) > 3)                                                                                                                         |
  |                                 ->  Gather Merge  (cost=13325.67..13430.49 rows=900 width=16) (actual time=82.259..82.259 rows=0 loops=241)                                                                    |
  |                                       Workers Planned: 2                                                                                                                                                       |
  |                                       Workers Launched: 2                                                                                                                                                      |
  |                                       ->  Sort  (cost=12325.64..12326.58 rows=375 width=16) (actual time=27.782..27.783 rows=0 loops=723)                                                                      |
  |                                             Sort Key: songs_1.artist_id                                                                                                                                        |
  |                                             Sort Method: quicksort  Memory: 25kB                                                                                                                               |
  |                                             Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                                                                    |
  |                                             Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                                                                    |
  |                                             ->  Hash Join  (cost=223.33..12309.61 rows=375 width=16) (actual time=27.754..27.754 rows=0 loops=723)                                                             |
  |                                                   Hash Cond: (playlist_songs_1.song_id = songs_1.id)                                                                                                           |
  |                                                   ->  Hash Join  (cost=214.93..12300.20 rows=375 width=8) (actual time=27.694..27.695 rows=0 loops=723)                                                        |
  |                                                         Hash Cond: (playlist_songs_1.playlist_id = playlists_1.id)                                                                                             |
  |                                                         ->  Parallel Seq Scan on playlist_songs playlist_songs_1  (cost=0.00..11036.93 rows=399193 width=16) (actual time=0.008..12.205 rows=317669 loops=723) |
  |                                                         ->  Hash  (cost=214.81..214.81 rows=9 width=8) (actual time=0.420..0.420 rows=0 loops=483)                                                             |
  |                                                               Buckets: 1024  Batches: 1  Memory Usage: 8kB                                                                                                     |
  |                                                               ->  Seq Scan on playlists playlists_1  (cost=0.00..214.81 rows=9 width=8) (actual time=0.420..0.420 rows=0 loops=483)                            |
  |                                                                     Filter: (creator_id = 2)                                                                                                                   |
  |                                                                     Rows Removed by Filter: 9585                                                                                                               |
  |                                                   ->  Hash  (cost=5.40..5.40 rows=240 width=16) (actual time=0.054..0.054 rows=241 loops=483)                                                                  |
  |                                                         Buckets: 1024  Batches: 1  Memory Usage: 20kB                                                                                                          |
  |                                                         ->  Seq Scan on songs songs_1  (cost=0.00..5.40 rows=240 width=16) (actual time=0.012..0.033 rows=241 loops=483)                                       |
  |                                                               Filter: (artist_id IS NOT NULL)                                                                                                                  |
  | Planning Time: 0.965 ms                                                                                                                                                                                        |
  | Execution Time: 19833.655 ms                                                                                                                                                                                   |
  ```

    - Index on playlists creator_id, this will hep find all the playlists by a specific creator faster. Also an index on playlist_songs song_id, this should just make the join faster when joining playlist_songs and songs. This should solve the main time lag which comes from joining playlist_songs and songs.
    - `CREATE INDEX idx_playlists_creator_id ON playlists(creator_id)` and `CREATE INDEX idx_playlist_songs_song_id ON playlist_songs(song_id)`
    - 
  ```
  | QUERY PLAN                                                                                                                                                                                                   |
  | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | Limit  (cost=20491.39..20491.40 rows=1 width=50) (actual time=7.678..10.639 rows=0 loops=1)                                                                                                                  |
  |   ->  Sort  (cost=20491.39..20491.40 rows=1 width=50) (actual time=7.676..10.637 rows=0 loops=1)                                                                                                             |
  |         Sort Key: songs.created_at DESC                                                                                                                                                                      |
  |         Sort Method: quicksort  Memory: 25kB                                                                                                                                                                 |
  |         ->  Nested Loop  (cost=13190.59..20491.38 rows=1 width=50) (actual time=7.665..10.626 rows=0 loops=1)                                                                                                |
  |               Join Filter: (songs.artist_id = users.id)                                                                                                                                                      |
  |               ->  Nested Loop Anti Join  (cost=13190.59..20429.42 rows=1 width=52) (actual time=7.665..10.625 rows=0 loops=1)                                                                                |
  |                     ->  Merge Join  (cost=13157.90..13272.46 rows=80 width=60) (actual time=7.664..10.623 rows=0 loops=1)                                                                                    |
  |                           Merge Cond: (songs.artist_id = songs_1.artist_id)                                                                                                                                  |
  |                           ->  Sort  (cost=14.89..15.49 rows=240 width=52) (actual time=0.088..0.088 rows=1 loops=1)                                                                                          |
  |                                 Sort Key: songs.artist_id                                                                                                                                                    |
  |                                 Sort Method: quicksort  Memory: 47kB                                                                                                                                         |
  |                                 ->  Seq Scan on songs  (cost=0.00..5.40 rows=240 width=52) (actual time=0.004..0.029 rows=241 loops=1)                                                                       |
  |                           ->  Unique  (cost=13143.01..13254.80 rows=62 width=8) (actual time=7.574..10.532 rows=0 loops=1)                                                                                   |
  |                                 ->  GroupAggregate  (cost=13143.01..13254.64 rows=62 width=8) (actual time=7.573..10.531 rows=0 loops=1)                                                                     |
  |                                       Group Key: songs_1.artist_id                                                                                                                                           |
  |                                       Filter: (count(DISTINCT playlist_songs_1.song_id) > 3)                                                                                                                 |
  |                                       ->  Gather Merge  (cost=13143.01..13247.83 rows=900 width=16) (actual time=7.572..10.529 rows=0 loops=1)                                                               |
  |                                             Workers Planned: 2                                                                                                                                               |
  |                                             Workers Launched: 2                                                                                                                                              |
  |                                             ->  Sort  (cost=12142.99..12143.92 rows=375 width=16) (actual time=0.250..0.254 rows=0 loops=3)                                                                  |
  |                                                   Sort Key: songs_1.artist_id                                                                                                                                |
  |                                                   Sort Method: quicksort  Memory: 25kB                                                                                                                       |
  |                                                   Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                                                            |
  |                                                   Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                                                            |
  |                                                   ->  Hash Join  (cost=40.67..12126.95 rows=375 width=16) (actual time=0.225..0.229 rows=0 loops=3)                                                          |
  |                                                         Hash Cond: (playlist_songs_1.song_id = songs_1.id)                                                                                                   |
  |                                                         ->  Hash Join  (cost=32.27..12117.55 rows=375 width=8) (actual time=0.071..0.074 rows=0 loops=3)                                                     |
  |                                                               Hash Cond: (playlist_songs_1.playlist_id = playlists_1.id)                                                                                     |
  |                                                               ->  Parallel Seq Scan on playlist_songs playlist_songs_1  (cost=0.00..11036.93 rows=399193 width=16) (actual time=0.017..0.017 rows=1 loops=3) |
  |                                                               ->  Hash  (cost=32.16..32.16 rows=9 width=8) (actual time=0.043..0.043 rows=0 loops=3)                                                         |
  |                                                                     Buckets: 1024  Batches: 1  Memory Usage: 8kB                                                                                             |
  |                                                                     ->  Bitmap Heap Scan on playlists playlists_1  (cost=4.35..32.16 rows=9 width=8) (actual time=0.043..0.043 rows=0 loops=3)               |
  |                                                                           Recheck Cond: (creator_id = 2)                                                                                                     |
  |                                                                           ->  Bitmap Index Scan on idx_playlists_creator_id  (cost=0.00..4.35 rows=9 width=0) (actual time=0.041..0.042 rows=0 loops=3)      |
  |                                                                                 Index Cond: (creator_id = 2)                                                                                                 |
  |                                                         ->  Hash  (cost=5.40..5.40 rows=240 width=16) (actual time=0.091..0.091 rows=241 loops=3)                                                            |
  |                                                               Buckets: 1024  Batches: 1  Memory Usage: 20kB                                                                                                  |
  |                                                               ->  Seq Scan on songs songs_1  (cost=0.00..5.40 rows=240 width=16) (actual time=0.015..0.053 rows=241 loops=3)                                 |
  |                                                                     Filter: (artist_id IS NOT NULL)                                                                                                          |
  |                     ->  Hash Join  (cost=32.69..240.58 rows=4 width=8) (never executed)                                                                                                                      |
  |                           Hash Cond: (playlist_songs.playlist_id = playlists.id)                                                                                                                             |
  |                           ->  Index Scan using idx_playlist_songs_song_id on playlist_songs  (cost=0.42..197.83 rows=3992 width=16) (never executed)                                                         |
  |                                 Index Cond: (song_id = songs.id)                                                                                                                                             |
  |                           ->  Hash  (cost=32.16..32.16 rows=9 width=8) (never executed)                                                                                                                      |
  |                                 ->  Bitmap Heap Scan on playlists  (cost=4.35..32.16 rows=9 width=8) (never executed)                                                                                        |
  |                                       Recheck Cond: (creator_id = 2)                                                                                                                                         |
  |                                       ->  Bitmap Index Scan on idx_playlists_creator_id  (cost=0.00..4.35 rows=9 width=0) (never executed)                                                                   |
  |                                             Index Cond: (creator_id = 2)                                                                                                                                     |
  |               ->  Seq Scan on users  (cost=0.00..44.76 rows=1376 width=22) (never executed)                                                                                                                  |
  | Planning Time: 1.367 ms                                                                                                                                                                                      |
  | Execution Time: 10.842 ms                                                                                                                                                                                    |
  ```
  - These two indexes cut the run time to the point where the main query runs in 11 ms, which is on par with the other endpoints.


- get spotlight list
  -
  ```
      | QUERY PLAN                                                                                                                                                     |
  | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Limit  (cost=13457.29..13457.30 rows=1 width=50) (actual time=575.661..603.166 rows=15 loops=1)                                                                |
  |   ->  Sort  (cost=13457.29..13457.30 rows=1 width=50) (actual time=575.659..603.163 rows=15 loops=1)                                                           |
  |         Sort Key: (random())                                                                                                                                   |
  |         Sort Method: quicksort  Memory: 27kB                                                                                                                   |
  |         ->  Nested Loop Anti Join  (cost=1214.92..13457.28 rows=1 width=50) (actual time=35.944..603.100 rows=15 loops=1)                                      |
  |               Join Filter: (playlist_songs.song_id = songs.id)                                                                                                 |
  |               Rows Removed by Join Filter: 601                                                                                                                 |
  |               ->  Nested Loop  (cost=0.00..62.34 rows=1 width=50) (actual time=0.102..1.357 rows=17 loops=1)                                                   |
  |                     Join Filter: (users.id = songs.artist_id)                                                                                                  |
  |                     Rows Removed by Join Filter: 11743                                                                                                         |
  |                     ->  Seq Scan on users  (cost=0.00..51.64 rows=116 width=22) (actual time=0.005..0.200 rows=294 loops=1)                                    |
  |                           Filter: (spotlight AND ((user_type = 'artist'::user_role) OR (user_type = 'listener_and_artist'::user_role)))                        |
  |                           Rows Removed by Filter: 1084                                                                                                         |
  |                     ->  Materialize  (cost=0.00..7.23 rows=2 width=44) (actual time=0.000..0.002 rows=40 loops=294)                                            |
  |                           ->  Seq Scan on songs  (cost=0.00..7.22 rows=2 width=44) (actual time=0.021..0.067 rows=40 loops=1)                                  |
  |                                 Filter: ((genre)::text = ANY ('{Country,"Hip Hop"}'::text[]))                                                                  |
  |                                 Rows Removed by Filter: 201                                                                                                    |
  |               ->  Gather  (cost=1214.92..13390.20 rows=900 width=8) (actual time=28.710..35.391 rows=35 loops=17)                                              |
  |                     Workers Planned: 2                                                                                                                         |
  |                     Workers Launched: 2                                                                                                                        |
  |                     ->  Hash Join  (cost=214.93..12300.20 rows=375 width=8) (actual time=25.274..30.596 rows=12 loops=51)                                      |
  |                           Hash Cond: (playlist_songs.playlist_id = playlists.id)                                                                               |
  |                           ->  Parallel Seq Scan on playlist_songs  (cost=0.00..11036.93 rows=399193 width=16) (actual time=0.008..14.137 rows=319346 loops=51) |
  |                           ->  Hash  (cost=214.81..214.81 rows=9 width=8) (actual time=0.419..0.419 rows=5 loops=35)                                            |
  |                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                   |
  |                                 ->  Seq Scan on playlists  (cost=0.00..214.81 rows=9 width=8) (actual time=0.411..0.412 rows=5 loops=35)                       |
  |                                       Filter: (creator_id = 1377)                                                                                              |
  |                                       Rows Removed by Filter: 9580                                                                                             |
  | Planning Time: 0.888 ms                                                                                                                                        |
  | Execution Time: 603.255 ms                                                                                                                                     |
  ```
  - Similar to get new releases, the indexes that would cut the time are ones on creator_id in playlists and song_id on playlist_songs, since the majority of the time comes from joins.
  - `CREATE INDEX idx_playlists_creator_id ON playlists(creator_id)` and `CREATE INDEX idx_playlist_songs_song_id ON playlist_songs(song_id)`
  -
  ```
      | QUERY PLAN                                                                                                                                                        |
  | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Limit  (cost=5760.23..5760.24 rows=1 width=50) (actual time=68.688..68.691 rows=15 loops=1)                                                                       |
  |   ->  Sort  (cost=5760.23..5760.24 rows=1 width=50) (actual time=68.687..68.689 rows=15 loops=1)                                                                  |
  |         Sort Key: (random())                                                                                                                                      |
  |         Sort Method: quicksort  Memory: 27kB                                                                                                                      |
  |         ->  Nested Loop Anti Join  (cost=79.91..5760.22 rows=1 width=50) (actual time=13.794..68.637 rows=15 loops=1)                                             |
  |               ->  Nested Loop  (cost=0.28..23.95 rows=1 width=50) (actual time=0.038..0.400 rows=17 loops=1)                                                      |
  |                     ->  Seq Scan on songs  (cost=0.00..7.22 rows=2 width=44) (actual time=0.031..0.167 rows=40 loops=1)                                           |
  |                           Filter: ((genre)::text = ANY ('{Country,"Hip Hop"}'::text[]))                                                                           |
  |                           Rows Removed by Filter: 201                                                                                                             |
  |                     ->  Index Scan using users_pkey1 on users  (cost=0.28..8.30 rows=1 width=22) (actual time=0.005..0.005 rows=0 loops=40)                       |
  |                           Index Cond: (id = songs.artist_id)                                                                                                      |
  |                           Filter: (spotlight AND ((user_type = 'artist'::user_role) OR (user_type = 'listener_and_artist'::user_role)))                           |
  |                           Rows Removed by Filter: 1                                                                                                               |
  |               ->  Hash Join  (cost=79.63..5736.25 rows=4 width=8) (actual time=4.011..4.011 rows=0 loops=17)                                                      |
  |                     Hash Cond: (playlist_songs.playlist_id = playlists.id)                                                                                        |
  |                     ->  Bitmap Heap Scan on playlist_songs  (cost=47.36..5693.50 rows=3992 width=16) (actual time=0.652..3.680 rows=3987 loops=17)                |
  |                           Recheck Cond: (song_id = songs.id)                                                                                                      |
  |                           Heap Blocks: exact=51722                                                                                                                |
  |                           ->  Bitmap Index Scan on idx_playlist_songs_song_id  (cost=0.00..46.36 rows=3992 width=0) (actual time=0.363..0.363 rows=3987 loops=17) |
  |                                 Index Cond: (song_id = songs.id)                                                                                                  |
  |                     ->  Hash  (cost=32.16..32.16 rows=9 width=8) (actual time=0.077..0.077 rows=5 loops=1)                                                        |
  |                           Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                            |
  |                           ->  Bitmap Heap Scan on playlists  (cost=4.35..32.16 rows=9 width=8) (actual time=0.071..0.072 rows=5 loops=1)                          |
  |                                 Recheck Cond: (creator_id = 1377)                                                                                                 |
  |                                 Heap Blocks: exact=1                                                                                                              |
  |                                 ->  Bitmap Index Scan on idx_playlists_creator_id  (cost=0.00..4.35 rows=9 width=0) (actual time=0.067..0.067 rows=5 loops=1)     |
  |                                       Index Cond: (creator_id = 1377)                                                                                             |
  | Planning Time: 1.860 ms                                                                                                                                           |
  | Execution Time: 68.834 ms                                                                                                                                         |
  ```
  - This cut the time down by almost a factor of 10, making it run at a fast enough time to compare to the other endpoints.

- add album to playlist
  - ```
  | QUERY PLAN                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------- |
| Insert on playlist_songs  (cost=21415.49..21415.51 rows=0 width=0) (actual time=80.749..80.750 rows=0 loops=1)                        |
|   InitPlan 1 (returns $0)                                                                                                             |
|     ->  Seq Scan on playlist_songs playlist_songs_1  (cost=0.00..21415.49 rows=1 width=0) (actual time=80.579..80.579 rows=0 loops=1) |
|           Filter: ((playlist_id = 423) AND (song_id = 30))                                                                            |
|           Rows Removed by Filter: 958033                                                                                              |
|   ->  Result  (cost=0.00..0.01 rows=1 width=32) (actual time=80.681..80.681 rows=1 loops=1)                                           |
|         One-Time Filter: (NOT $0)                                                                                                     |
| Planning Time: 0.465 ms                                                                                                               |
| Trigger for constraint playlist_songs_playlist_id_fkey: time=0.299 calls=1                                                            |
| Trigger for constraint playlist_songs_song_id_fkey: time=0.110 calls=1                                                                |
| Execution Time: 81.218 ms                                                                                                             |
  ```
  - This endpoint first uses a simple select from albums with a join on songs to get all songs from a given album. This part has minimal impact because it only uses primary keys for joining and filtering. 
  - After getting the songs for an album an insert query is run for each of those songs, adding them if the song does not already exist in the playlist. This query can be repeated as many times as there are songs in a given album and slow down the endpoint. To speed this end we should add an index playlist_songs song_id to speed up the NOT EXISTS part of each of these repeated queries.
  - `CREATE INDEX idx_playlist_songs_song_id ON playlist_songs(song_id)`
  - ```
  | QUERY PLAN                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Insert on playlist_songs  (cost=6346.15..6346.16 rows=0 width=0) (actual time=11.972..11.974 rows=0 loops=1)                                     |
|   InitPlan 1 (returns $0)                                                                                                                        |
|     ->  Bitmap Heap Scan on playlist_songs playlist_songs_1  (cost=46.34..6346.15 rows=1 width=0) (actual time=11.690..11.691 rows=0 loops=1)    |
|           Recheck Cond: (song_id = 31)                                                                                                           |
|           Filter: (playlist_id = 423)                                                                                                            |
|           Rows Removed by Filter: 4032                                                                                                           |
|           Heap Blocks: exact=3119                                                                                                                |
|           ->  Bitmap Index Scan on idx_playlist_songs_song_id  (cost=0.00..46.33 rows=3988 width=0) (actual time=0.809..0.809 rows=4032 loops=1) |
|                 Index Cond: (song_id = 31)                                                                                                       |
|   ->  Result  (cost=0.00..0.01 rows=1 width=32) (actual time=11.812..11.813 rows=1 loops=1)                                                      |
|         One-Time Filter: (NOT $0)                                                                                                                |
| Planning Time: 0.795 ms                                                                                                                          |
| Trigger for constraint playlist_songs_playlist_id_fkey: time=0.745 calls=1                                                                       |
| Trigger for constraint playlist_songs_song_id_fkey: time=0.268 calls=1                                                                           |
| Execution Time: 13.163 ms                                                                                                                        |
  ```
  - This index significantly reduced the execution time for this part of the endpoint and matches the indexes added above which works nicely because we didn't need to add too many new indexes.
