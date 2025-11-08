from Repositorio.repoElectro import electroRepo
from Repositorio.labRepo import quimicaRepo
from Servicio.serviceElectro import serviceElectro
from Conexiones.conexion import Conexion
from Modelos.element import UniqueItem, StockItem
from Repositorio.userRepo import UserRepo
from Modelos.users import User, Alumno
from Modelos.registro import RegistroBase
from Controller.controllerElectroyLab import controller
conexion = Conexion("postgresql://postgres.gzzjbgubbqptkmydmper:panconqueso123@aws-1-us-east-2.pooler.supabase.com:5432/postgres")
repo_electro = electroRepo("electromecanica",conexion)
repo_quimica = quimicaRepo("quimica", conexion)
repo_usuario = UserRepo("usuarios",conexion)
serviceElectromecanica = serviceElectro(repo_electro,repo_usuario)

tabla_stock = "inventario_stock"
tabla_unicos = "inventario_unicos"

stick= StockItem(
        nombre="martillo",
        descripcion="Herramienta manual para tornillos planos",
        estado="operativo",
        ubicacion="Taller 1",
        ubicacion_interna="Estante A",
        tipo="stock",
        cantidad=25,
        disponibles=20,
        isReusable=True
    )
unico = UniqueItem(
        nombre="Cable eléctrico 1.5mm",
        descripcion="Rollo de cable de cobre aislado",
        estado="operativo",
        ubicacion="Depósito",
        ubicacion_interna="Estante B",
        tipo="unico",
        codigo_interno= "12339"
    )
registrobase = RegistroBase(
    element_id=13,
    cantidad=10,
    destino="7mo5ta"
)
usuario = User(
    nombre="tomas",
    apellido="sanchez",
    

)
#
# print(repo_usuario.crearUsuario(usuario))
serviceElectromecanica.crear_registro(registrobase,usuario)

#serviceElectromecanica.crear_elemento(stick)
#print(serviceElectromecanica.ver_elemento(11))
#print(serviceElectromecanica.ver_registros())


