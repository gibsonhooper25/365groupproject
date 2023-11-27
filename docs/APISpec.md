# API Specification
## 1. Songs
### 1.1 Show Songs `/songs/` - GET
Allows users to see all songs available on the database

Returns: 
```commandline
[
    {
        title: <string>,
        artist: <string>,
        album: <string>,
        genre: <genre>,
        duration: <int>
    }
]
```
### 1.2 Get Song - `/songs/{song_id}` - GET
Gets full information about a single song

Returns:
```commandline
{
    song: <string>,
    genre: <genre>,
    duration: <int>,
    album: <string>,
    artist: <string>
}
```
### 1.3 Create Song (Single) - `/songs/new` - POST
Creates a new song, unassociated with an album

Input:
```commandline
{
  artist_id: <id>,
  song: {
    title: <name>,
    genre: <enum>,
    moods: <list[Mood]>
    duration: <int>
  }
}
```
Returns:
```commandline
{
    song_id: <id>
}
```
### 1.4 Comment - `/songs/{song_id}/comment/new` - POST
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
### 1.5 Rate/Feedback - `/songs/{song_id}/rate` - POST
Allows user to leave a rating from 1 to 5 on a song and some feedback with the rating. There is enumerated feedback categories based on common feedback.
For example, feedback could be "melody", "sound quality" or even "overall".

Input:
```commandline
{
    rating: <int 1 to 5>,
    feedback_category: <enum>
    user: <user_id>
}
```
Returns:
```commandline
"Thank you for your feedback"
```
### 1.6 View Ratings and Feedback - `/songs/{song_id}/reviews` - GET
Allows user to view the average rating score for one song.

Returns:
```commandline
{
    avg_rating: <float>
}
```
### 1.7 Search for song by name - `/songs/search/name` - GET
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
### 1.8 Search for songs by genre - `/songs/search/genre` - GET
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

## 2. Albums
### 2.1 Get Album - `/albums/{album_id}` - GET
Gets all songs in an album

Returns:
```commandline
[
    {
        title: <string>,
        genre: <genre>,
        duration: <int>
    }
]
```
### 2.2 Create Album - `/albums/new` - POST
Creates a new album.

Input:
```commandline
{
    artist_id: <id>,
    name: <name>,
    genre: <enum>
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
"ok" 
```
### 2.4 Rate/Feedback - `/albums/{album_id}/rate` - POST
Allows user to leave a rating from 1 to 5 on an album and some feedback with the rating. There is enumerated feedback categories based on common feedback.
For example, feedback could be "melody", "sound quality" or even "overall".

Input:
```commandline
{
    rating: <int 1 to 5>,
    feedback_category: <enum>
    user: <user_id>
}
```
Returns:
```commandline
"Thank you for your feedback"
```
### 2.5 View Ratings and Feedback - `/albums/{album_id}/reviews` - GET
Allows creator to view the ratings and feedback categories for one of their songs or albums.

Returns:
```commandline
{
    avg_rating: <float>
}
```

## 3. Playlists
### 3.1 Get Playlist - `/playlist/{playlist_id}` - GET
Returns the playlist with the given playlist_id.
```commandline
[
    {
        title: <string>,
        genre: <genre>,
        duration_seconds: <int>
    }
]
```
### 3.2 Create Curated Playlist - `/playlist/new/curated` - PUT
Generates a list of songs from the given parameters and saves it to the backend.

Input:
```commandline
{
    user_id: <user id>,
    title: <string>
    mood: <mood enum>,
    length: <int>
}
```
Returns:
```commandline
{
    playlist: <playlist id>
}
```
### 3.3 Create Personal Playlist - `/playlist/new/personal` - POST
Allows users to create empty playlists for them to populate themselves.

Input:
```commandline
{
  listener: <bool>,
  email: <string>,
  password: <string>,
  name: <string>,
  mood: <mood>
}
```
Returns:
```commandline
{
    playlist: <playlist id>
}
```
### 3.4 Update Playlist - `/playlist/{playlist_id}/add-song/{song_id}` or `/playlist/{playlist_id}/add-songs/{album_id}` - POST
Allows the user to add a song or all songs in an album to a pre-existing playlist.

Returns:
```commandline
{
    success: <boolean>
}
```
### 3.5 Remove Song - `playlist/{playlist_id}/remove-song/{song_id}` - DELETE
Allows user to remove a song from their playlist

Returns:
```commandline
"Removed song from playlist"
```

## 4. Users

### 4.1 Create User - `/users` - POST
Creates a new user if not already in the database.

Input:
```commandline
{
    name: <string>,
    email: <string>,
    username: <string>,
    password: <string>,
    user_type: <user_role enum>

}
```
Returns:
```commandline
{
    "user_id": <int>
}
```
### 4.2 Delete User - `/users/{user_id}` - DELETE
Deletes a user from database.

Returns:
```commandline
{
    success: <boolean>
}
```
## 5. Discovery

### 5.1 Create User Preferences - `/discovery/{user_id}` - POST
Creates default user preferences if they do not exist yet.

Input:
```commandline
{
    user_id: <int>

}
```
Returns:
```commandline
"Preferences successfully set."
```
### 5.2 Get Preferences - `/discovery/preferences/{user_id}` - GET
Gets users current preferences

Input:
```commandline
{
    user_id: <int>

}
```
Returns:
```commandline
{
    genres: <list>
    moods: <list>
}
```

### 5.3 Add Preferences - `/discovery/preferences/{user_id}` - POST
Adds a user preference.

Input:
```commandline
{
    user_id: <int>
    update_type: <preference enum>
    update: <mood or genre enum>
}
```
Returns:
```commandline
"Preference updated"
```
### 5.4 Delete Preferences - `/discovery/preferences/{user_id}` - DELETE
Deletes a user preference.

Input:
```commandline
{
    user_id: <int>
    update_type: <preference enum>
    update: <mood or genre enum>
}
```
Returns:
```commandline
"Preference updated"
```
### 5.5 Discovery Feed - `/discovery/new_releases/{user_id}` - GET
Provides discovery feed: songs based on mood and genre preferences, new artists based on genre preferences, and new releases from liked artists.
Input:
```commandline
{
    user_id: <int>
}
```
Returns:
```commandline
[
    "Songs you might enjoy based on current preferences"
    [
        {
            title: <str>
            artist: <str>
            genre: <genre enum>
            duration: <int>
            release_date: <str>
        }
    ]
    "Some new artists you might enjoy"
    [
        artist: <str>
    ]
    "New releases from artists you love"
    [
        {
            title: <str>
            artist: <str>
            genre: <genre enum>
            duration: <int>
            release_date: <str>
        }
    ]
]
```
### 5.6 Add Artist to Spotlight - `/discovery/spotlight/add` - PATCH
Adds an artist to spotlight

Input:
```commandline
{
    user_id: <int>
    description: <str>
}
```
Returns:
```commandline
"Spotlight given to user: user_id"
```
### 5.7 Remove Artist From Spotlight - `/discovery/spotlight/remove` - PATCH
Removes an artist from spotlight

Input:
```commandline
{
    user_id: <int>
}
```
Returns:
```commandline
"Spotlight removed from user: user_id"
```
### 5.8 Get Spotlight List - `/discovery/spotlight/{user_id}` - GET
Gets songs that are promoted through the spotlight list which are in lighn with a users genres
Input:
```commandline
{
    user_id: <int>
}
```
Returns:
```commandline
[
    {
        title: <str>
        artist: <str>
        genre: <genre enum>
        duration: <int>
        release_date: <str>
    }
]
```
