# Example Flows
## Example 1
- Listener wants to exercise for 30 minutes, so they want to create a 12 song playlist
  - calls `/playlist/new/curated` with parameters `length=12`, `mood=ENERGETIC` also providing user ID and a name for the playlist
- They especially like one of the songs on this playlist, so they click on it to view more information
  - `/songs/{song_id}` shows them the song information
- They decide to leave a 5-star review on this song
  - `/songs/{song_id}/rate` with parameter `rating=5`
  - this takes them to `/songs/{song_id}/rate/5/feedback` where they can select a feedback category to submit

## Example 2
- Jake is a picky listener who only listens to songs that fit his current vibe. As a person who already knows his music tastes, he wants to make his own playlist and add entire albums to his list at once, so that he can easily build lists with songs from artists he likes. To do this he starts by creating an empty playlist
  - calls `/playlist/new/personal` providing his user ID and a name for the playlist
- With the playlist ID that was returned to Jake, he can begin adding songs or entire albums to the list
  - to add one song, he calls `/playlist/{playlist_id}/add-song/{song_id}`
  - to add all songs in an album, he calls `/playlist/{playlist_id}/add-songs/{album_id}`
- Once Jake thinks he has finished adding the songs he likes to his new playlist he can view the masterpeice he has created
  - to see his playlist he calls `/playlist/{playlist_id}`

## Example 3
- Bill Wurtz is a song artist known for creating very unique songs. Bill is releasing a new album and would like add it to Harmony API and see what people think of it. To add his new album bill will first create the album and the songs then add each of the songs to the album.
  - Bill creates the album with `/albums/new` providing his artist ID, the genre, and a name for the album
  - Bill creates each of the songs for the album using `/songs/new` again providing his artist ID, the genre, and the name of the song
  - Bill then adds each of these songs to this new album with `/albums/{album_id}/add-song/{song_id}`
- After waiting a while for Harmony API users to provide ratings and feedback Bill will get an idea of how people like his new album
  - Bill veiws ratings and feedback for his new album with `/albums/{album_id}/reviews`
- Bill wants to narrow down what songs people did and didn't like in his new album and goes to look at ratings and feedback for individual songs
  - Bill veiws ratings and feedback for each song in the new album with `/songs/{song_id}/reviews`
- Satisfied that he knows what he did right and where he went wrong, Bill is ready to go off and write more song content
