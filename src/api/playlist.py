from fastapi import APIRouter, Depends
from src.api import auth

router = APIRouter(
    prefix="/playlists",
    tags=["playlists"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/new/curated")
def create_curated_playlist():
    pass

@router.post("/new/personal")
def create_personal_playlist():
    pass

@router.post("/{playlist_id}/add-song/{song_id}")
def add_song_to_playlist():
    pass

@router.post("/{playlist_id}/add-songs/{album_id}")
def add_album_songs_to_playlist():
    pass

@router.get("/{playlist_id}")
def get_playlist():
    pass