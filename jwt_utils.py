from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "CHANGE_ME"
ALGORITHM = "HS256"

def create_access_token(username: str):
    return jwt.encode(
        {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None