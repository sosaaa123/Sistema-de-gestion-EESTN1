from repo_imports import *
from service_imports import *
from controller_imports import *
from Conexiones.conexion import Conexion
from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from Servicio.pwdManager import PasswordManager
from Servicio.tokenManager import TokenManager

load_dotenv()
var= os.getenv("DATABASE_URL")
conexion=Conexion(var)
algoritmo = os.getenv("ALGORITHM")
secret_key = os.getenv("JWT_SECRET_KEY")

pm = PasswordManager()
tm = TokenManager(algoritmo,secret_key)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_methods = ["*"],
    allow_credentials = True, 
    allow_headers = ["*"],
)
#----------USUARIOS-------------
repositorio_usuarios = UserRepo("usuarios",conexion)
service_usuarios = Userservice(conexion,repositorio_usuarios, pm, tm)
controller_usuarios = userController(service_usuarios,"/usuarios")
controller_usuarios.rutas(app)

#-------ELECTROMECANICA------------
repositorio_electromecanica = electroRepo("electromecanica",conexion)
service_electromecanica = serviceElectro(repositorio_electromecanica,repositorio_usuarios)
controller_electromecanica = controllerElectroyLab(service_electromecanica,"/electromecanica")
controller_electromecanica.rutas(app)

#-----------QUIMICA----------------
repositorio_quimica = quimicaRepo("quimica",conexion)
serive_quimica = serviceQuimica(repositorio_quimica,repositorio_usuarios)
controller_quimica = controllerElectroyLab(serive_quimica,"/quimica")
controller_quimica.rutas(app)

#--------BIBLIOTECA---------------
repositorio_biblioteca = BiblioRepo("biblioteca",conexion)
service_biblioteca = BiblioService(repositorio_biblioteca,repositorio_usuarios)
controller_biblioteca = BiblioController(service_biblioteca)
controller_biblioteca.rutas(app)

#-------PROGRAMACION-----------------
repositorio_programacion = PrgRepo("programacion", conexion)
service_programacion = Servicio(repositorio_programacion, repositorio_usuarios)
controller_programacion = Controller(service_programacion,"/programacion")
controller_programacion.rutas(app)