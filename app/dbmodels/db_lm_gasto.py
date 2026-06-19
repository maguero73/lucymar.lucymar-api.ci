from sqlalchemy import Column, Integer, Numeric, DateTime, String, Float, func, extract
from app.core.database import DBBase
from datetime import datetime, timedelta, timezone, date
from sqlalchemy.orm import Session

ARG_TZ = timezone(timedelta(hours=-3))  # UTC-3 Argentina



class DBLMGasto(DBBase):
    __tablename__ = "lm_gastos"

    id = Column(Integer, primary_key=True, index=True)
    cod_gasto = Column(Integer)
    cod_titular = Column(Integer)   
    monto = Column(Float)
    fecha = Column(DateTime)
    codigo_moneda =Column(String(3))
    tipo_cambio =Column(Float)
    fecha_creacion = Column(
    DateTime,
    nullable=False,
    default=lambda: datetime.now(ARG_TZ)
    )

#-------------------------------------------------------------------

def get_gastos(session: Session, offset:int=0, limit:int=1000):
    query=session.query(DBLMGasto).offset(offset).limit(limit).all()
    return query

#-------------------------------------------------------------------
#-------------------------------------------------------------------
def get_gastos_por_moneda(session: Session, tipo_moneda: str):
    """
    Ejemplo de filter + all():
    Devuelve UNA LISTA de todos los gastos que coincidan con la moneda.
    Si no hay coincidencias, devuelve una lista vacía [].
    """
    query = session.query(DBLMGasto).filter(DBLMGasto.codigo_moneda == tipo_moneda).all()
    return query

#-------------------------------------------------------------------
def get_gasto_por_id(session: Session, id_gasto: int):
    """
    Ejemplo de filter + first():
    Devuelve UN SOLO objeto (el primero que encuentre) o None si no existe.
    Ideal para buscar por Primary Key o campos únicos.
    """
    # Opción 1: Usando filter().first()
    gasto = session.query(DBLMGasto).filter(DBLMGasto.id == id_gasto).first()
    
    # Opción 2 (Más directa para PKs): session.query(DBLMGasto).get(id_gasto)
    return gasto

#-------------------------------------------------------------------
def buscar_gasto_especifico(session: Session, cod_titular: int, monto_minimo: float):
    """
    Ejemplo de filtros múltiples + first():
    Busca el PRIMER gasto que cumpla TODAS las condiciones.
    Útil para verificar existencia o traer un caso representativo.
    """
    gasto = session.query(DBLMGasto).filter(
        DBLMGasto.cod_titular == cod_titular,
        DBLMGasto.monto > monto_minimo
    ).first()
    
    return gasto



#--------------------------------------------------------------------
def get_gastos_mayor_a(session: Session, monto_minimo: float):
    """
    Caso de Uso: Alertas de Gastos Altos
    Devuelve todos los gastos que superan cierto monto.
    Uso de filter + all()
    """
    return session.query(DBLMGasto).filter(DBLMGasto.monto > monto_minimo).all()

#--------------------------------------------------------------------
def get_ultimo_gasto_titular(session: Session, cod_titular: int):
    """
    Caso de Uso: Actividad Reciente
    Devuelve el último gasto registrado por un titular.
    Uso de filter + order_by + first()
    """
    return session.query(DBLMGasto)\
        .filter(DBLMGasto.cod_titular == cod_titular)\
        .order_by(DBLMGasto.fecha.desc())\
        .first()
#-----------------------------------------------------------------------------
def get_gastos_filtrados(
    session: Session, fecha_desde: date = None, fecha_hasta: date = None,
    cod_titular: list[int] = None, cod_gasto: list[int] = None, 
    codigo_moneda: str = None
):
    """
    Construye una query dinámica aplicando filtros solo si se proporcionan.
    """
    query = session.query(DBLMGasto)

    if fecha_desde:
        query = query.filter(DBLMGasto.fecha >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(DBLMGasto.fecha <= fecha_hasta)

    if cod_titular:
        # Si es una lista, usamos IN
        query = query.filter(DBLMGasto.cod_titular.in_(cod_titular))
    
    if cod_gasto:
        query = query.filter(DBLMGasto.cod_gasto.in_(cod_gasto))

    if codigo_moneda:
        query = query.filter(DBLMGasto.codigo_moneda == codigo_moneda)

    return query.all()

#-----------------------------------------------------------------------------
def get_gastos_anuales(
    session: Session,
    cod_titular: int = 0,
    cod_gasto: int = 0
):

    query = session.query(
        extract('year', DBLMGasto.fecha).label('anio'),
        func.sum(DBLMGasto.monto).label('total')
    )

    if cod_titular != 0:
        query = query.filter(
            DBLMGasto.cod_titular == cod_titular
        )

    if cod_gasto != 0:
        query = query.filter(
            DBLMGasto.cod_gasto == cod_gasto
        )

    return (
        query
        .group_by(extract('year', DBLMGasto.fecha))
        .order_by(extract('year', DBLMGasto.fecha))
        .all()
    )


#-----------------------------------------------------------------------------
def get_anios(session: Session):

    return (
        session.query(
            extract('year', DBLMGasto.fecha).label('anio')
        )
        .distinct()
        .order_by('anio')
        .all()
    )
