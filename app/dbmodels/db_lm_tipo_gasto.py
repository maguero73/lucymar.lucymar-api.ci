from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from app.core.database import DBBase


class DBLMTipoGasto(DBBase):
    __tablename__ = "lm_tipo_gasto"

    codigo = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(50), nullable=False)
    
#------------------------------------------------------------------------
def get_tipos_gasto(session:Session, offset:int = 0, limit: int = 1000):
    query = session.query(DBLMTipoGasto).offset(offset).limit(limit).all()
    return query

#------------------------------------------------------------------------
def get_descripcion_tipo(session: Session, codigo: int) -> str:
    """
    Caso de Uso: Obtener nombre legible
    Busca un tipo de gasto por ID y devuelve su descripción.
    Uso de filter + first()
    """
    tipo = session.query(DBLMTipoGasto).filter(DBLMTipoGasto.codigo == codigo).first()
    
    if tipo:
        return tipo.descripcion
    return "Desconocido"

#------------------------------------------------------------------------


