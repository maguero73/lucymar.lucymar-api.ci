from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import SessionLocal
from app.dbmodels.db_lm_gasto import DBLMGasto
from datetime import datetime
from typing import List
from app.dbmodels import db_lm_gasto
import pytz

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- MODELO DE ENTRADA ---
class GastoIn(BaseModel):
    cod_gasto: int
    cod_titular: int
    monto: float
    fecha: datetime
    codigo_moneda: Optional[str] = None
    tipo_cambio: float

# --- MODELO DE SALIDA

class GastoOut(BaseModel):
    id: int
    cod_gasto: int
    cod_titular: int
    monto: float    
    fecha: datetime
    codigo_moneda: Optional[str] = None
    tipo_cambio: float

    class Config:
        from_attributes = True


#--------------------------------------------------------------------------------------
@router.get ("/api/gastos",response_model=List[GastoOut])

async def listar_gastos(
    request:Request,
    offset: int = 0,
    limit: int = 1000,
    db: Session = Depends (get_db)
):
    try:
        return db_lm_gasto.get_gastos(session=db, offset=offset, limit=limit)
    
    except Exception as e:
        print("🔥 ERROR detectado:", e)
        import traceback
        traceback.print_exc()

#----------------------------------------------------------------------------------------

@router.post("/api/gastos")
async def crear_gasto(gasto: GastoIn, db: Session = Depends(get_db)):
    try:
        print("Gasto recibido:", gasto)


        # Fecha de creación LA GENERA EL BACKEND
        argentina = pytz.timezone("America/Argentina/Buenos_Aires")
        fecha_creacion = datetime.now(argentina)
        
        nuevo_gasto = DBLMGasto(
            cod_gasto=gasto.cod_gasto,
            cod_titular=gasto.cod_titular,
            monto=gasto.monto,
            fecha=gasto.fecha,
            codigo_moneda=gasto.codigo_moneda,
            tipo_cambio=gasto.tipo_cambio,
            fecha_creacion=fecha_creacion,
        )


        db.add(nuevo_gasto)
        db.commit()

        return {"mensaje": "Gasto guardado con éxito"}
    
    
    except Exception as e:
        db.rollback()
        print("Error en test insert:", e)
        raise HTTPException(status_code=500, detail="Error al crear gasto")