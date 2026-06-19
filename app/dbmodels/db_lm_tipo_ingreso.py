from sqlalchemy import Column, Integer, String
from app.core.database import DBBase  # ajusta esto según tu estructura
from sqlalchemy.orm import Session

#--------------------------------------------------------------------------------------
class DBLMTipoIngreso(DBBase):
    __tablename__ = "lm_tipo_ingreso"

    codigo = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(50), nullable=False)

#-------------------------------------------------------------------------------------
def get_tipos_ingreso(session:Session, offset:int = 0, limit: int = 1000):
    query = session.query(DBLMTipoIngreso).offset(offset).limit(limit).all()
    return query

#-------------------------------------------------------------------------------------
