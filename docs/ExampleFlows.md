# Example Flows
## Example 1
- Listener wants to exercise for 30 minutes, so they want to create a 12 song playlist
  - calls `/playlist/new` with parameters `length=12`, `mood=ENERGETIC`
- They especially like one of the songs on this playlist, so they click on it to view more information
  - `/songs/{song_id}` shows them the song information
- They decide to leave a 5-star review on this song
  - `/songs/{song_id}/rate` with parameter `rating=5`
  - this takes them to `/songs/{song_id}/rate/5/feedback` where they can select a feedback category to submit

