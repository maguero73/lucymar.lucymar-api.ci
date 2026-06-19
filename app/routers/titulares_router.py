from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.dbmodels import db_lm_titular
from typing import List

router = APIRouter()

def get_db():
    db =SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/titulares",responses={
        200: { "model": List }})
async def listar_titulares(request:Request, offset: int = 0, limit: int = 1000, session: Session = Depends (get_db)):
    try:
        return db_lm_titular.get_titulares(session=session, offset=offset, limit=limit)
    except Exception as e:
        print("🔥 ERROR detectado:", e)
        import traceback
        traceback.print_exc()