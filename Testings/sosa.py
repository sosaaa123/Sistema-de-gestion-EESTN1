from Conexiones.conexion import Conexion
from Controller.userController import userController
from Repositorio.userRepo import UserRepo
from Repositorio.biblioRepo import BiblioRepo
from Repositorio.repositorio import Repositorio
from Modelos.users import User, Alumno, Profesor, Personal
from Modelos.registro import RegistroBase
from Modelos.element import StockItem, UniqueItem
from Modelos.biblioteca import Libro
from Controller.biblioController import BiblioController
from Controller.controller import Controller
from Servicio.pwdManager import PasswordManager
from Servicio.tokenManager import TokenManager
from fastapi.middleware.cors import CORSMiddleware
#30/9 ver funciones insert into(prevenir inyecciones sql)

#Cambie todas las tablas a:
#inventario, uniqueitems, stockitems
#puedo hacer un repositorioGeneral, los demas heredan de el

#Notas para hacer el servicio:
#Considerar el caso de que se ingresa un nuevo elemento, el objeto que se ingresa se carga como disponible
from fastapi import FastAPI
from Servicio.biblioService import BiblioService
from Servicio.servicio import Servicio
from Servicio.userService import Userservice
from datetime import datetime, time
from dotenv import load_dotenv
import os
#uvicorn Testings.sosa:app --reload --host 0.0.0.0 --port 8000

#tengo que crear tabla libros, tabla registros, tabla, uniqueItem_library, stockItem_library
#27/9 voy a probar los metodos de repositorio creo q ya lo termino hoy y empiezo el service

#Para tabla areas
# (id: 1) Biblioteca
# (id: 2) Laboratorio
# (id: 3) Electromecanica
# (id: 4) Programacion


load_dotenv()
var= os.getenv("DATABASE_URL")
conexion=Conexion(var)
algoritmo = os.getenv("ALGORITHM")
secret_key = os.getenv("JWT_SECRET_KEY")

repositorioPrg = Repositorio("programacion", conexion)
rep_usuarios = UserRepo("usuarios", conexion)

pm = PasswordManager()
tm = TokenManager(algoritmo, secret_key)


serviceUser = Userservice(conexion, rep_usuarios, pm, tm)


#15
#password: panconqueso12
#email: lautasosita0999@gmail.com
#print(serviceUser.crearJerarquia(15, "panconqueso12", "administrador","lautasosita0999@gmail.com" ,["programacion"]))

biblio_rep = BiblioRepo("biblioteca", conexion)

servicioPrg = Servicio(repositorioPrg, rep_usuarios)

biblioteca_servicio = BiblioService(biblio_rep, rep_usuarios)




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_methods = ["*"],
    allow_credentials = True, 
    allow_headers = ["*"],
)

controllerPrg = BiblioController(servicioPrg, "/programacion")
controllerPrg.rutas(app)

controllerBiblio = Controller(biblioteca_servicio, "/biblioteca")
controllerBiblio.rutas(app)

controllerUsers = userController(serviceUser, "/usuarios")
controllerUsers.rutas(app)

