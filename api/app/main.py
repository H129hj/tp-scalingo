from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app import schemas
from app.config import get_settings
from app.db import get_db
from app.models import Note, User
from app.security import create_token, current_user, hash_password, verify_password

app = FastAPI(title="TP Scalingo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.post("/auth/register", response_model=schemas.Token, status_code=201)
def register(body: schemas.Credentials, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == body.email.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email deja utilise")
    user = User(email=body.email.lower(), password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    return schemas.Token(access_token=create_token(user.id))


@app.post("/auth/login", response_model=schemas.Token)
def login(body: schemas.Credentials, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")
    return schemas.Token(access_token=create_token(user.id))


@app.get("/notes", response_model=list[schemas.NoteOut])
def list_notes(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Note).where(Note.owner_id == user.id).order_by(Note.id.desc())).all()


@app.post("/notes", response_model=schemas.NoteOut, status_code=201)
def create_note(body: schemas.NoteIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    note = Note(owner_id=user.id, title=body.title, body=body.body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if note is None or note.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note introuvable")
    db.delete(note)
    db.commit()
