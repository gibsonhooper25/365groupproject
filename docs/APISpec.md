# API Specification
## 1. Listeners
### 1.1 Get Song - `/songs/{song_id}` or `/albums/{album_id}/songs/{song_id}` - GET
### 1.2 Get Songs By Artist - `/artists/{artist_id}/songs` - GET
Allows user to retrieve all songs by a specific artist.

Returns: 
```commandline
{
    songs: <list>
}
```
### 1.3 Get Album - `/albums/{album_id}` - GET
### 1.4 Get Playlist - `/playlist/{playlist_id}` - GET
Returns the playlist with the given playlist_id.
```commandline
{
    name: <string>,
    songs: <list>
}
```
### 1.5 Create Curated Playlist - `/playlist/new/curated` - PUT
Generates a list of songs from the given parameters and saves it to the backend.

Input:
```commandline
{
    user: <user id>,
    mood: <mood enum>,
    name: <string>,
    length: <int>
}
```
Returns:
```commandline
{
    Playlist: <playlist id>
}
```
### 1.6 Create Personal Playlist - `/playlist/new/personal` - POST
Allows users to create empty playlists for them to populate themselves.

Input:
```commandline
{
    user: <user id>,
    name: <string>
}
```
Returns:
```commandline
{
    Playlist: <playlist id>
}
```
### 1.7 Update Playlist - `/playlist/{playlist_id}/add-song/{song_id}` or `/playlist/{playlist_id}/add-songs/{album_id}` - POST
Allows the user to add a song or all songs in an album to a pre-existing playlist.

Returns:
```commandline
{
    success: <boolean>
}
```

### 1.8 Comment - `/songs/{song_id}/comment/new` or `/albums/{album_id}/songs/{song_id}/comment/new` - POST
Allows the user to post a comment to the discussion thread for a given song.

Input:
```commandline
{
    user: <user>,
    comment: <string>
}
```
Returns:
```commandline
{
    success: <boolean>
}
```
### 1.9 Rate/Feedback - `/songs/{song_id}/rate` or `/albums/{album_id}/rate` - POST
Allows user to leave a rating from 1 to 5 on a song or album and some feedback after they give it a rating. There will be enumerated feedback categories based on what the rating was.
For example, a rating 1 category could be "Poor Sound Quality" while a rating 5 category could be "Excellent Lyricism".

Input:
```commandline
{
    rating: <int 1 to 5>,
    feedback: <enum>
}
```
### 1.10 Search for song by name - `/songs/search/name` - GET
Allows users to search for song(s) by name.

Input:
```commandline
{
    name: <name>
}
```
Returns:
```commandline
{
    songs: <list>
}
```
### 1.11 Search for songs by genre - `/songs/search/genre` - GET
Allows users to search for a bredth of songs by genre

Input:
```commandline
{
    genre: <genre>
}
```
Returns:
```commandline
{
    songs: <list>
}
```

## 2. Creators
### 2.1 Create Song (Single) - `/songs/new` - POST
Creates a new song, unassociated with an album

Input:
```commandline
{
  artist_ids: [<id>, ...],
  song: {
    title: <name>,
    genre: <enum>,
    duration: <int>
  }
}
```
### 2.2 Create Album - `/albums/new` - POST
Creates a new album.

Input:
```commandline
{
    artist_id: <id>,
    genre: <enum>,
    name: <name>
}
```

Returns:
```commandline
{
    album_id: <id>
}
```
### 2.3 Add Song to Album - `/albums/{album_id}/add-song/{song_id}` - POST
Adds song to given album

Returns:
```commandline
{
    success: <boolean>
}
```
### 2.4 View Ratings and Feedback - `/songs/{song_id}/reviews` or `/albums/{album_id}/reviews` - GET
Allows creator to view the ratings and feedback categories for one of their songs or albums.

Returns:
```commandline
{
    average_rating: <float>,
    <enum_1>: <int>
    <enum_2>: <int>
    .
    .
    .
}
```


## 3. Admins

### 3.1 Create User - `/users` - POST
Creates a new user if not already in the database.

Input:
```commandline
{
    name: <string>,
    email: <string>,
    username: <string>,
    password: <string>

}
```
Returns:
```commandline
{
    success: <boolean>
}
```
### 3.2 Delete User - `/users/{user_id}` - DELETE
Deletes a user from database.

Returns:
```commandline
{
    success: <boolean>
}
```

