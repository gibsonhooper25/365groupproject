from fastapi import APIRouter, Depends
from pydantic import BaseModel, conint
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from enum import Enum

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

class user_role(str, Enum):
    artist = "artist"
    listener = "listener"

@router.post("/")
def add_user(email: str, password: str, name:str, user_type: user_role, username: str):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
               """
                SELECT email FROM users WHERE email = :email
               """
            ), [{"email": email}]) 
            if result.rowcount != 0:
               return "Account with given email already exists."
            
            result = connection.execute(sqlalchemy.text(
               """
                SELECT username FROM users WHERE username = :username
               """
            ), [{"username": username}])
            if result.rowcount != 0:
                return "Account with given username already exists."
            
            connection.execute(sqlalchemy.text(
                """
                WITH salt AS (SELECT gen_salt('md5') AS salt)
                INSERT INTO users (email, password, salt, name, user_type, username)
                VALUES (:email, crypt(:password, (SELECT salt FROM salt)), (SELECT salt FROM salt), 
                :name, :user_type, :username)
                """
            ), [{"email": email, "password": password, "name": name, "user_type": user_type, "username": username}])
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"
   
    return "Account successfully created."


@router.post("/login")
def log_in(username: str, password: str):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                """
                    SELECT password, salt FROM users
                    WHERE username = :username
                """
            ),[{"username": username}])
            if result.rowcount == 0:
                return "Invalid username"
            result = result.first()
           
            attempt = connection.execute(sqlalchemy.text(
                """
                    SELECT crypt(:password, :salt) AS attempted_password
                """
            ),[{"password": password, "salt": result.salt}])
            attempt = attempt.first()
            if attempt.attempted_password == result.password:
                return "ok"
            else:
                return "incorrect password"
          
    except DBAPIError as error:
        return f"Error returned: <<<{error}>>>"
   
