# Example workflow
- Listener wants to exercise for 30 minutes, so they want to create a 12 song playlist
  - calls `/playlist/new/curated` with parameters `length=12`, `mood=energetic` also providing user ID and a name for the playlist
- They especially like one of the songs on this playlist, so they choose to view more information
  - `/songs/{song_id}/reviews` shows them the song's reviews
- They decide to leave a 5-star review on this song
  - `/songs/{song_id}/rate` with parameter `rating=5` and `feedback=melody`

# Testing results
1. `/playlist/new/curated`
Curl:
```
curl -X 'POST' \
  'https://harmony-api-service.onrender.com/playlists/new/curated?user_id=2&title=Workout&mood=energetic&length=12' \
  -H 'accept: application/json' \
  -H 'access_token: harmony' \
  -d ''
```

Response:
```
{
  "Playlist": 7
}
```

2. `/songs/21/reviews`
Curl:
```
curl -X 'GET' \
  'https://harmony-api-service.onrender.com/songs/21/reviews' \
  -H 'accept: application/json'
```

Response:
```
{
  "avg_rating": "5.00"
}
```

3. `/songs/21/rate`
Curl:
```
curl -X 'POST' \
  'https://harmony-api-service.onrender.com/songs/21/rate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "rating": 5,
  "feedback_category": "melody",
  "user": 2
}'
```

Response:
```
"Thank you for your feedback"
```

# Example workflow 2
- Jake is a picky listener who only listens to songs that fit his current vibe. As a person who already knows his music tastes, he wants to make his own playlist and add entire albums to his list at once, so that he can easily build lists with songs from artists he likes. To do this he starts by creating an empty playlist
  - calls `/playlist/new/personal` providing his user email and password and a name for the playlist
- With the playlist ID that was returned to Jake, he can begin adding songs or entire albums to the list
  - to add one song, he calls `/playlist/{playlist_id}/add-song/{song_id}`
  - to add all songs in an album, he calls `/playlist/{playlist_id}/add-songs/{album_id}`
- Once Jake thinks he has finished adding the songs he likes to his new playlist he can view the masterpeice he has created
  - to see his playlist he calls `/playlist/{playlist_id}`

# Testing results
1. `/playlist/new/personal`
Curl:
```
curl -X 'POST' \
  'https://harmony-api-service.onrender.com/playlists/new/personal' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "listener": true,
  "email": "jakemertens@example.com",
  "password": "BaconPancakes",
  "name": "MyPlaylist",
  "mood": "happy"
}'
```

Response:
```
{
  "Playlist": 8
}
```

2. `/playlist/8/add-song/19`
Curl:
```
curl -X 'POST' \
  'https://harmony-api-service.onrender.com/playlists/8/add-song/19' \
  -H 'accept: application/json' \
  -d ''
```

Response:
```
"Song added to playlist"
```

3. `/playlist/8/add-songs/1`
Curl:
```
curl -X 'POST' \
  'https://harmony-api-service.onrender.com/playlists/8/add-songs/1' \
  -H 'accept: application/json' \
  -d ''
```

Response:
```
"Added album to playlist"
```

4. `/playlist/8`
Curl:
```
curl -X 'GET' \
  'https://harmony-api-service.onrender.com/playlists/8' \
  -H 'accept: application/json'
```

Response:
```
{
  "Name": "MyPlaylist",
  "Songs": [
    {
      "title": "Uptown Girl",
      "genre": "Pop",
      "duration_seconds": 194
    },
    {
      "title": "The Stranger",
      "genre": "Rock",
      "duration_seconds": 310
    },
    {
      "title": "Only the Good Die Young",
      "genre": "Rock",
      "duration_seconds": 235
    },
    {
      "title": "Scenes from an Italian Restaurant",
      "genre": "Jazz",
      "duration_seconds": 456
    },
    {
      "title": "Movin' Out",
      "genre": "Rock",
      "duration_seconds": 210
    },
    {
      "title": "Vienna",
      "genre": "Rock",
      "duration_seconds": 214
    },
    {
      "title": "We Didn't Start The Fire",
      "genre": "Pop",
      "duration_seconds": 287
    }
  ]
}
```
