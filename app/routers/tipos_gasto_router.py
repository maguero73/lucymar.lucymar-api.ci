from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.dbmodels import db_lm_tipo_gasto
from typing import List

router = APIRouter()

def get_db():
    db =SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/tipos-gasto",responses={
        200: { "model": List }})
async def listar_tipos_gasto(request:Request, offset: int = 0, limit: int = 1000, session: Session = Depends (get_db)):
    try:
        
        return db_lm_tipo_gasto.get_tipos_gasto(session=session, offset=offset, limit=limit)
    
    except Exception as e:
        print("🔥 ERROR detectado:", e)
        import traceback
        traceback.print_exc()