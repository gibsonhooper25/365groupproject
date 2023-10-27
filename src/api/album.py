from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/albums",
    tags=["albums"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/new")
def create_new_album():
    pass