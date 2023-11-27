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

### Diagram

## Case 3
### Description

### Diagram