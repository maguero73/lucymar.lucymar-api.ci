from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Reemplazá estos datos con los de tu entorno real
ORACLE_USER = "ora"
ORACLE_PASSWORD = "ora"
ORACLE_HOST = "10.30.205.232"
ORACLE_PORT = "1521"
ORACLE_SID = "fisco"  # o el SERVICE_NAME, como "orclpdb1"

# 🔧 URL para conexión a Oracle
DATABASE_URL = (
    f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/?service_name={ORACLE_SID}"

)

# Crear el engine
engine = create_engine(DATABASE_URL, echo=True)

# Crear una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()




#INTENTAR UNA CONSULTA BASICA A LA BASE
"""

try:
    with engine.connect() as connection:
        result=connection.execute(text("SELECT 1"))
        print("conexion exitosa:", result.scalar())
except Exception as e:
    print("Error al conectar:", e)        

"""