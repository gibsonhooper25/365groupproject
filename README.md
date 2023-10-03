## Contributors
Gibson Hooper: gdhooper@calpoly.edu

Ashton Mitchell: amitch35@calpoly.edu

Ella Hagen: elhagen@calpoly.edu

Andy Cristales: agcrista@calpoly.edu

## Project Description
Welcome to Harmony API, a revolutionary service designed to bring the world of music to your fingertips. With Harmony API, you have the power to explore, create, and share your musical journey effortlessly. Our API offers a comprehensive relational database that connects artists, albums, and tracks. Harmony API allows you to dive into a vast collection of artists and albums, discovering the beats that resonate with your soul. You can also craft your playlists, share your musical stories, and curate soundtracks for every moment. Harmony API can even generate personalized playlists based on your preferences. Whether you are a music enthusiast, developer, or curator, join us in creating a harmonious world of music, where every user becomes a creator, every track finds its listener, and every moment has its perfect sound.
The service will be backed by a database composed of the following relations, queryable and mutable via mySQL:
1. Artist Table:

   Fields: ArtistID (Primary Key), Name, Genre, etc.
   
3. Album Table:

    Fields: AlbumID (Primary Key), Title, ReleaseYear, ArtistID (Foreign Key), etc.
   
5. Track Table:

    Fields: TrackID (Primary Key), Title, Duration, AlbumID (Foreign Key), etc.
   
7. User Table:

    Fields: UserID (Primary Key), Username, Email, Password, etc.
   
9. Playlist Table:

    Fields: PlaylistID (Primary Key), Name, UserID (Foreign Key), etc.
   
11. PlaylistTrack Table (Associative Table for Many-to-Many Relationship):

    Fields: PlaylistID (Foreign Key), TrackID (Foreign Key), Order (to define the order of tracks in a playlist), etc.
   
