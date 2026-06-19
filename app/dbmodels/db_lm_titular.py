from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from app.core.database import DBBase

#------------------------------------------------------------------------
class DBLMTitular(DBBase):
    __tablename__ = "lm_titular"

    codigo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(20))

#------------------------------------------------------------------------
def get_titular(session: Session, id: int):
    return session.query(DBLMTitular).filter(DBLMTitular.codigo==id).first()


#------------------------------------------------------------------------

def get_titulares(session:Session, offset:int = 0, limit: int = 1000):
    query = session.query(DBLMTitular).offset(offset).limit(limit).all()
    return query

#-------------------------------------------------------------------------

def get_descripcion_titular(session: Session, codigo: int) -> str:
    """
    Caso de Uso: Obtener nombre legible
    Busca un titular por ID y devuelve su nombre.
    Uso de filter + first()
    -> str
    Esto indica el tipo de retorno esperado de la función.

    Significa: “Esta función devuelve un string”

    No es obligatorio, pero es muy buena práctica.
    """
    titular = session.query(DBLMTitular).filter(DBLMTitular.codigo == codigo).first()
    
    if titular:
        return titular.nombre
    return "Desconocido"