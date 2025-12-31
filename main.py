from fastapi import FastAPI, Depends, HTTPException,Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import text
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

from db import SessionLocal

class QuestionRequest(BaseModel):
    question: str


SECRET_KEY = "super-long-random-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="JWT Secured QnA API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login",
                                     scheme_name="JWT Login")


def create_access_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # replace with DB validation later
    if form_data.username != "admin" or form_data.password != "admin123":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(form_data.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/questions", response_class=PlainTextResponse)
def get_all_questions():
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT question FROM geo.tbglqna")
        ).scalars().all()

        return "\n".join(result)
    finally:
        db.close()



@app.post("/get-answer")
def get_answer(
    question: str,
    current_user: str = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        # 1️ Get answer for asked question
        result = db.execute(
            text("""
                SELECT id, answer
                FROM geo.tbglqna
                WHERE question = :q
                LIMIT 1
            """),
            {"q": question}
        ).mappings().first()

        if not result:
            raise HTTPException(status_code=404, detail="Answer not found")

        # 2 Get next 3 unrelated questions
        next_questions = db.execute(
            text("""
                SELECT question
                FROM geo.tbglqna
                WHERE question != :q
                  AND isactive = true
                ORDER BY createddate DESC
                LIMIT 3
            """),
            {"q": question}
        ).scalars().all()

        return {
            "user": current_user,
            "question": question,
            "answer": result["answer"],
            "next_questions": next_questions
        }

    finally:
        db.close()
