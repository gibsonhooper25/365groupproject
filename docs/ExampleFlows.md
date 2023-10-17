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
  - calls `/playlist/{playlist_id}`
