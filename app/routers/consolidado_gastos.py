from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from pydantic import BaseModel
from app.core.database import SessionLocal
from sqlalchemy import text
from typing import Any, List
from datetime import date, datetime
from typing import Optional
from app.dbmodels import db_lm_gasto, db_lm_titular


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# ----- MODELO DE ENTRADA -----
class FiltroConsolidado(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    cod_titular: list[int]
    cod_gasto: list[int]
    codigo_moneda: str


# ---MODELO DE SALIDA ---
class ResultadosSalida(BaseModel):
    titular: str
    cod_gasto: int
    codigo_moneda: str
    monto: float
    fecha: date



# --- ENDPOINT FINAL OPTIMIZADO ---
@router.post("/api/consolidado_gastos", response_model=List[ResultadosSalida])
async def obtener_consolidado(filtros: FiltroConsolidado, db=Depends(get_db)):
    """
    Endpoint optimizado que delega el filtrado a la base de datos usando SQLAlchemy.
    """
    try:
        # Llamamos a la función del modelo que ya aplica los filtros en la query
        gastos_filtrados = db_lm_gasto.get_gastos_filtrados(
            session=db,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            cod_titular=filtros.cod_titular,
            cod_gasto=filtros.cod_gasto,
            codigo_moneda=filtros.codigo_moneda
        )

        # Mapeamos los resultados al modelo de salida
        resultados = [
            ResultadosSalida(
                titular=db_lm_titular.get_descripcion_titular(db, g.cod_titular),
                cod_gasto=g.cod_gasto,
                codigo_moneda=g.codigo_moneda,
                monto=g.monto,
                fecha=g.fecha.date() if isinstance(g.fecha, datetime) else g.fecha # Manejo seguro de fechas
            )
            for g in gastos_filtrados
        ]

        return resultados

    except Exception as e:
        print("🔥 ERROR en consolidado_gastos:", e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))