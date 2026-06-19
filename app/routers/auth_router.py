from fastapi import APIRouter
from app.auth.auth import crear_token
from fastapi import APIRouter, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "mariano" or form_data.password != "1234":
        print(f"Usuario recibido: {username}, Contraseña recibida: {password}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = crear_token({"sub": form_data.username, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}
