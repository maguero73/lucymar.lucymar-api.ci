from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
import os

#URL DE CONEXION
#DATABASE_URL = "mariadb+mariadbconnector://root:Admin@localhost:3306/lucymar_db"
#DATABASE_URL= "mysql://root:Dimaria123@localhost:3306/lucymar_db?allowPublicKeyRetrieval=true&useSSL=false"
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Dimaria123@localhost:3306/lucymar_db"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Dimaria123")
DB_NAME = os.getenv("DB_NAME", "lucymar_db")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


#CREAR EL MOTOR (engine)
engine=create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True, #podes poner False si no queres ver las consultas en consola
    pool_pre_ping=True,
    pool_recycle=3600
)


#engine = create_engine(SQLALCHEMY_DATABASE_URL)



#CREAR UNA SESION LOCAL PARA USAR EN CADA REQUEST

SessionLocal =sessionmaker(autocommit=False, autoflush=False, bind=engine)

#BASE PARA DEFINIR TUS MODELOS ORM

DBBase = declarative_base()



# Intentar una consulta básica
'''
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Conexión exitosa:", result.scalar())
except Exception as e:
    print("Error al conectar:", e)
'''