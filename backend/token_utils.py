from datetime import datetime, timedelta
import time

from fastapi import HTTPException
from jose import JWTError, jwt

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def check_token(access_token: str, refresh_token: str):
    try:
        decoded_access_token = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
        if decoded_access_token["exp"] < time.time():
            try:
                decoded_refresh_token = jwt.decode(refresh_token, SECRET_KEY, ALGORITHM)
                if decoded_refresh_token["exp"] < time.time():
                    raise HTTPException(status_code=401, detail="Access Token has expired")
                else:
                    return (create_token({"username": decoded_refresh_token["sub"]["username"]},
                                         timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
                            create_token({"username": decoded_refresh_token["sub"]["username"]},
                                         timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)))
            except JWTError:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
        else:
            return access_token, refresh_token
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")