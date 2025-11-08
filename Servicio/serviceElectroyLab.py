import logging
from Repositorio.repoElectroyLab import RepoGeneral
from Repositorio.userRepo import UserRepo
from Servicio.userService import Userservice
from Modelos.electro import StockItem, UniqueItem
from Modelos.registro import Registro, RegistroBase
from Modelos.users import User, Profesor
from datetime import datetime, time


def returm(succes:bool, mensaje: str, data):
    return{
        "succes":succes,
        "mensaje":mensaje,
        "data":data
    }
def calcular_fecha_y_hora():
    ahora = datetime.now()
    fecha = ahora.date()
    hora = ahora.time()
    expiracionn = None
    turnos = [
        (time(7,40), time(11,40)),
        (time(13,10), time(17,20)),
        (time(17,40), time(21,30))
    ]
    for inicio, fin in turnos:
        if inicio< hora < fin:
            expiracionn = fin

    return fecha,hora,expiracionn

class Service():
    def __init__(self, repo: RepoGeneral, userservice:Userservice):
        self.repo = repo
        self.userservice = userservice
    def crear_elemento(self, data):
        try:
            
            elementos = self.repo.ver_inventario() or []
           
            print(elementos)
            dataDic= data.dict()
            print (dataDic)
            for campos, valor in dataDic.items():
                if isinstance(valor,(str)) and not valor:
                    raise ValueError(f'el campo: {campos} no puede estar vacio' )
                if isinstance(valor,(int)) and  valor <0:
                    raise ValueError(f'el campo: {campos} no puede estar vacio' )
            for elemento in elementos:
                if elemento.nombre == dataDic["nombre"]:
                    raise ValueError("herramienta ya existente")
            self.repo.crear_elemento(data)
            return returm(True,f'elemento creado a la perfeccion', None)
        except Exception as e:
            logging.error(f'error al crear elemento: {e}') 
            return returm(False,f'error al crear nuevo elemento',None)     
    def ver_elementos(self):
        try:
            elementos = self.repo.ver_inventario()
            if  elementos is None:
                raise ValueError("elementos  no regstradas")
            return returm(True,f'elementos traidos correctamente', elementos)
        except Exception as e:
            logging.error(f'error al buscar los elementos: {e}')
            return returm(False,f'no se pudieron traer los elementos: {e}',None)
    def ver_elemento(self, identificador):
        try:
            elemento = self.repo.ver_elemento(identificador)
            if elemento is None:
                raise ValueError("no se encontro ninguna herramienta con ese nombre")
            return returm(True,f'elemento traido correctamente', elemento)
        except Exception as e:
            logging.error(f'error al buscar elemento: {e}')
            return returm(False,f'no se pudo traer el elemento: {e}',None)
    def eliminar_elemento(self, id_elemento:int):
        try:
            elemento = self.repo.ver_elemento(id_elemento)
            self.repo.eliminar_elemento(id_elemento, elemento.tipo)
            return returm(True,f'{elemento.nombre} elemento eliminado correctamente', None)
        except Exception as e:
            return returm(False,f'error al eliminar el elemento: {elemento.nombre}', None)
    def __verificar_disponibles(self,id_elemento:int ,cantidadPedidos: int):
        try:
            elemento = self.repo.ver_elemento(id_elemento)
            print (f'{cantidadPedidos} = {elemento.disponibles} ')
            if (elemento.tipo == "stock"):
                if (int(elemento.disponibles) >= int(cantidadPedidos)):
                    nuevaCantidad = elemento.disponibles - cantidadPedidos
                    self.repo.actualizar_disponibles(id_elemento,nuevaCantidad)
                    return True
                elif(elemento.disponibles == 0):
                    self.repo.actualizar_estado_id(id_elemento,"No disponible",elemento.tipo)
                    return False
            elif (elemento.tipo == "unico"):
                if (elemento.estado != "Disponible"):
                    return False
                elif (elemento.estado == "Disponible"):
                    self.repo.actualizar_estado("En curso", id_elemento, elemento.tipo)
                    return True
        except Exception as e:
            raise ValueError(f'error: {e}')
    def __verificar_y_relacionar_usuario(self, dataUser):
        try:
            usuario = dataUser.id_usuario
            print(usuario)
            if usuario == None:
                usuario = self.userservice.crearUsuario(dataUser)
            else:
                return usuario
            
               
        except Exception as e:
            raise ValueError(f'error en la capa electro service en el metodo verificar usuario: {e}')
    def crear_registro(self,data: RegistroBase ,dataUsuario:User):
        try:
            fechas = calcular_fecha_y_hora()
            estado = "En curso"
            usuario = self.__verificar_y_relacionar_usuario(dataUsuario)
            canridadPedidaDisponibles = self.__verificar_disponibles(data.element_id,data.cantidad)
            if canridadPedidaDisponibles is True:
                registro = Registro(
                        element_id =data.element_id,
                        cantidad= data.cantidad,
                        destino=data.destino,
                        usuario_id= usuario,
                        fecha=fechas[0] ,
                        hora= fechas[1],
                        expiracion=fechas[2] ,
                        estado = estado,
                    )
                self.repo.crear_registro(registro)
            else:
                raise ValueError("no hay suficientes herramientas para saciar el pedido")    
        except Exception as e:
            logging.error(f"error en la capa electro service en el metodo crear registro stock: {e}")
    def ver_registros(self):
        try:
            registros = self.repo.ver_registros()
            if registros is not None:
                return returm(True,f'registros traidos con exito', registros)
            else:
                return returm(False,f'error al traer los registros',None)
        except Exception as e:
            logging.error(f'error al traer registros: {e}')
    def devoluciones(self,id_registro:int):
        try:
            registro = self.repo.ver_registro(id_registro)
            elementoPrestado = self.repo.ver_elemento(registro.element_id)
            if (elementoPrestado.tipo == "stock"):
                if elementoPrestado.isReusable is True:
                    cantidadOriginal = elementoPrestado.disponibles + registro.cantidad
                    self.repo.actualizar_disponibles(cantidadOriginal,registro.element_id)
                    self.repo.actualizar_estado_id(registro.element_id, "Disponible")
                    self.repo.actualizar_estado_registro("Terminado",id_registro)
                else:
                    ValueError("tu herramienta no es reusable y no se puede devolver")
            elif (elementoPrestado.tipo == "unico"):
                self.repo.actualizar_estado_id(registro.element_id,"Disponible")
                self.repo.actualizar_estado_registro("Terminado",id_registro)
                
        except Exception as e:
            logging.ERROR(f"error al querer devolver un elemento: {e}")