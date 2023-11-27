## Case 1
### Description
A non-repeatable read could occur in the advanced playlist creation because of its dependency on average song rating.
The initial query in the advanced playlist creation returns only songs that have above a 4.0 rating in a given feedback category. If this query is made,
then a separate transaction submits feedback that drops the song's average rating below 4.0, the service will still place this song in the playlist
despite it having a rating that is too low.
### Diagram
![img.png](concurrency1.png)
## Case 2
### Description
A phantom read could occur in the get new releases function because it depends on the user preferences table. If a user deletes one of their preferences in between the stages of fetching preferences and generating recommendations, the result will contain their original preferences instead of their new ones.
### Diagram
<img width="1184" alt="concurrency2" src="https://github.com/gibsonhooper25/Harmony-API/assets/113931989/d12f8b01-8277-4821-abea-3dd3ebd2bfc3">

## Case 3
### Description

### Diagram
