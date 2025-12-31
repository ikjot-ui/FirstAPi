from fastapi import Header, HTTPException, Depends
from jwt_utils import verify_access_token

def jwt_required(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid header")

    user = verify_access_token(authorization.split(" ")[1])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user