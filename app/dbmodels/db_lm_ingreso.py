from sqlalchemy import Column, Integer, Numeric, DateTime, String, Float
from app.core.database import DBBase
from datetime import datetime, timedelta, timezone, date
from sqlalchemy.orm import Session

ARG_TZ = timezone(timedelta(hours=-3))  # UTC-3 Argentina



class DBLMIngreso(DBBase):
    __tablename__ = "lm_ingresos"

    id = Column(Integer, primary_key=True, index=True)
    cod_ingreso = Column(Integer)
    cod_titular = Column(Integer)   
    monto = Column(Float)
    fecha = Column(DateTime)
    cod_moneda =Column(String(3))
    tipo_cambio =Column(Float)
    fecha_creacion = Column(
    DateTime,
    nullable=False,
    default=lambda: datetime.now(ARG_TZ)
    )

#--------------------------------------------------------------------
def get_ingresos(session: Session, offset:int=0, limit:int=1000):
    query=session.query(DBLMIngreso).offset(offset).limit(limit).all()
    return query

#--------------------------------------------------------------------
def get_ingresos_por_moneda(session: Session, codigo_moneda: str):
    """
    Caso de Uso: Reporte por Divisa
    Devuelve todos los ingresos en una moneda específica (ej. 'USD').
    """
    return session.query(DBLMIngreso).filter(DBLMIngreso.cod_moneda == codigo_moneda).all()

#--------------------------------------------------------------------
def get_ingresos_del_mes(session: Session, anio: int, mes: int):
    """
    Caso de Uso: Cierre Mensual
    Devuelve los ingresos dentro de un rango de fechas (mes completo).
    """
    # Crear fecha inicio (día 1 del mes)
    fecha_inicio = datetime(anio, mes, 1)
    
    # Calcular fecha fin (día 1 del mes siguiente)
    if mes == 12:
        fecha_fin = datetime(anio + 1, 1, 1)
    else:
        fecha_fin = datetime(anio, mes + 1, 1)
        
    # Filtramos: fecha >= inicio Y fecha < fin
    return session.query(DBLMIngreso).filter(
        DBLMIngreso.fecha >= fecha_inicio,
        DBLMIngreso.fecha < fecha_fin
    ).all()

#------------------------------------------------------------------------

def get_ingresos_filtrados(
    session: Session, fecha_desde: date = None, fecha_hasta: date = None,
    cod_titular: list[int] = None, cod_ingreso: list[int] = None, 
    codigo_moneda: str = None
):
    """
    Construye una query dinámica aplicando filtros solo si se proporcionan.
    """
    query = session.query(DBLMIngreso)

    if fecha_desde:
        query = query.filter(DBLMIngreso.fecha >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(DBLMIngreso.fecha <= fecha_hasta)

    if cod_titular:
        # Si es una lista, usamos IN
        query = query.filter(DBLMIngreso.cod_titular.in_(cod_titular))
    
    if cod_ingreso:
        query = query.filter(DBLMIngreso.cod_gasto.in_(cod_ingreso))

    if codigo_moneda:
        query = query.filter(DBLMIngreso.codigo_moneda == codigo_moneda)

    return query.all()