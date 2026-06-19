################################################    -----pruebas_mariano   ---############################################################
import traceback
from contextlib import asynccontextmanager


from app.curso_python.geometria import area_circulo, perimetro_circulo


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
#from app.endpoints import titulares
#from app.endpoints import tipo_gasto
from app.routers import gasto_router, ingreso_router, auth_router, consolidado_gastos, consolidado_ingresos, titulares_router, tipos_gasto_router, tipos_ingreso_router, reportes_negocio
#from app.endpoints import tipo_ingreso
from app.middlewares.audit_middleware_auth import JWTMiddleware


from fastapi.security import HTTPBearer
from fastapi.security import OAuth2PasswordBearer



#from app.helpers import token_preprocess
from app.routers import auth_router #prueba_mariano


app= FastAPI(title="Backend-FastAPI")




bearer_scheme = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

#----------------------------Middleware---------------------------------------------#

#app.add_middleware(JWTMiddleware, database_service='desa@fiscodb')

#---------------------------Services--------------------------------------------
# Conexiones a BD
#app.add_services_from_path(database_service.Database,'conf/ds/')



#----------------------------Routers----------------------------------------

app.include_router(titulares_router.router, tags=["Titulares"]) #dependencies=[Depends(oauth2_scheme)])
app.include_router(gasto_router.router, tags=["Gastos"]) #dependencies=[Depends(bearer_scheme)])
app.include_router(tipos_gasto_router.router, tags=["Gastos"]) #dependencies=[Depends(bearer_scheme)])
app.include_router(ingreso_router.router, tags=["Ingresos"])#dependencies=[Depends(bearer_scheme)])
app.include_router(tipos_ingreso_router.router, tags=["Ingresos"])#dependencies=[Depends(bearer_scheme)])
app.include_router(consolidado_gastos.router, tags=["Gastos"])#dependencies=[Depends(bearer_scheme)])
app.include_router(consolidado_ingresos.router, tags=["Ingresos"])#dependencies=[Depends(bearer_scheme)])
app.include_router(reportes_negocio.router, tags=["Reportes"])#dependencies=[Depends(bearer_scheme)])



#------------------------Auths Login-------------------------------------------

app.include_router(auth_router.router, tags=["Auth"])#dependencies=[Depends(bearer_scheme)])




# ------------------------- Middlewares --------------------------------------------------------

# -------- CORS (cross origin resource sharing) -----------------------------------
origins = [
        "http://localhost:5173"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # O "*" si estas probando
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



print(area_circulo(3))
print(perimetro_circulo(3))