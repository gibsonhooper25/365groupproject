# Example workflow
- Bill Wurtz is a song artist known for creating very unique songs. Bill is releasing a new album and would like add it to Harmony API and see what people think of it. To add his new album bill will first create the album and the songs then add each of the songs to the album.
  - Bill creates the album with `/albums/new` providing his artist ID, the genre, and a name for the album
  - Bill creates each of the songs for the album using `/songs/new` again providing his artist ID, the genre, and the name of the song
  - Bill then adds each of these songs to this new album with `/albums/{album_id}/add-song/{song_id}`
- After waiting a while for Harmony API users to provide ratings and feedback Bill will get an idea of how people like his new album
  - Bill veiws ratings and feedback for his new album with `/albums/{album_id}/reviews`
- Bill wants to narrow down what songs people did and didn't like in his new album and goes to look at ratings and feedback for individual songs
  - Bill veiws ratings and feedback for each song in the new album with `/songs/{song_id}/reviews`
- Satisfied that he knows what he did right and where he went wrong, Bill is ready to go off and write more song content

# Testing results
1. `/albums/new`
Curl:
```
curl -X 'POST' \
  'https://harmony-api-service.onrender.com/albums/new' \
  -H 'accept: application/json' \
  -H 'access_token: harmony' \
  -H 'Content-Type: application/json' \
  -d '{
  "artist_id": 1,
  "name": "Alphabet Shuffle - Single",
  "genre": "Indie"
}'
```
Response:
```
{
  "album_id": 2
}
```

2. `/songs/new`
Curl:
```
curl -X 'POST' \
  'https://harmony-api-service.onrender.com/songs/new' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "
  "artist_id": 1,
  "song": {
    "title": "Alphabet Shuffle",
    "genre": "Indie",
    "duration": 60
  }
}'
```
Response:
```
{
  "song_id": 11
}
```

3. `/albums/2/add-song/11`
Curl:
```
curl -X 'POST' \
  'https://harmony-api-service.onrender.com/albums/2/add-song/11' \
  -H 'accept: application/json' \
  -d ''
```
Response:
```
"ok"
```

4. `/albums/2/reviews`
Curl:
```
curl -X 'GET' \
  'https://harmony-api-service.onrender.com/albums/2/reviews' \
  -H 'accept: application/json'
```
Response:
```
{
  "avg_rating": "3.00"
}
```

5. `/songs/11/reviews`
Curl:
```
curl -X 'GET' \
  'https://harmony-api-service.onrender.com/songs/11/reviews' \
  -H 'accept: application/json' 
```
Response:
```
{
  "avg_rating": "5.00"
}
```
