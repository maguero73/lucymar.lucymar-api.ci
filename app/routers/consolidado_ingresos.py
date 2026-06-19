from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from pydantic import BaseModel
from app.core.database import SessionLocal
from sqlalchemy import text
from typing import Any, List
from datetime import date, datetime
from typing import Optional
from app.dbmodels import db_lm_ingreso, db_lm_titular


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
    cod_ingreso: list[int]
    codigo_moneda: str


# ---MODELO DE SALIDA ---
class ResultadosSalida(BaseModel):
    titular: str
    cod_ingreso: int
    codigo_moneda: str
    monto: float
    fecha: date



# --- ENDPOINT FINAL OPTIMIZADO ---
@router.post("/api/consolidado_ingresos", response_model=List[ResultadosSalida])
async def obtener_consolidado(filtros: FiltroConsolidado, db=Depends(get_db)):
    """
    Endpoint optimizado que delega el filtrado a la base de datos usando SQLAlchemy.
    """
    try:
        # Llamamos a la función del modelo que ya aplica los filtros en la query
        ingresos_filtrados = db_lm_ingreso.get_ingresos_filtrados(
            session=db,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            cod_titular=filtros.cod_titular,
            cod_ingreso=filtros.cod_ingreso,
            codigo_moneda=filtros.codigo_moneda
        )

        # Mapeamos los resultados al modelo de salida
        resultados = [
            ResultadosSalida(
                titular=db_lm_titular.get_descripcion_titular(db, i.cod_titular),
                cod_ingreso=i.cod_ingreso,
                codigo_moneda=i.codigo_moneda,
                monto=i.monto,
                fecha=i.fecha.date() if isinstance(i.fecha, datetime) else i.fecha # Manejo seguro de fechas
            )
            for i in ingresos_filtrados
        ]

        return resultados

    except Exception as e:
        print("🔥 ERROR en consolidado_gastos:", e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))