# User Stories
1. As a lover of a very broad range of music, I want to separate lists of songs, so that I can listen to just a particular genre.
2. As a newcomer to the music scene, I want to have a set of music chosen for me, so that I can discover new music I might like.
3. As a picky listener, I want to make my own playlists of songs, so that I can listen to songs that fit my current vibe.
4. As a person who already knows my music tastes, I want to add entire albums to my lists at once, so that I can easily build lists with songs from artists I like.
5. As an avid blogger, I want to share stories and thoughts about particular music and artists, so that I can express my opinions.
6. As an artist, I want to be able to see listening statistics for my music, so that I understand what my listeners are more likely to listen to. 
7. As a casual listener, I want to explore curated playlists based on moods or activities, so that I can easily find music that suits different occasions.
8. As a social music enthusiast, I want to connect with friends and see their music preferences, so that I can discover new songs through their recommendations.
9. As a mobile user, I want to have a seamless experience switching between devices, so that I can continue listening to my music without interruption.
10. As an audiophile, I want to have access to high-quality audio streaming options, so that I can enjoy my favorite songs with superior sound.
11. As a music event attendee, I want to receive notifications about upcoming concerts or events featuring my favorite artists, so that I can plan to attend.
12. As a language learner, I want to discover and explore music in different languages, so that I can improve my language skills while enjoying diverse genres.

# Exceptions/Error Scenarios
1. If a user asks for a playlist generated based on their tastes without any songs associated with that user, it will give back an error to the user and ask them to add some songs they like.
2. If a song uploaded by an artist is deemed unfit by an administrator, it will notify the artist with an error that the song violates Harmony-API's guidelines.
3. If an artist tries uploading a song and it fails (ex. poor connection), it will give back an error to the artist and will ask them to try uploading again.
4. If a user tries to access a song that has been removed by either the artist or an administrator, it will give back an error that the song is not available to listen to at the moment.
5. If a user tries to delete a shared playlist, it will give back an error that the playlist is shared and requires permission from both users. It will then send a notification to all users who share the playlist asking for permission to delete. 
6. If an artist tries to upload a song in the wrong format, it will return an error to the artist and ask them to resubmit with an audio format approved by Harmony-API.
7. x
8. x
9. x
10. x
11. x
12. x
