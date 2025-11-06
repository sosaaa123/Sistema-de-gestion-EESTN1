from typing import Any
from Repositorio.repositorio import Repositorio
from Repositorio.userRepo import UserRepo
from datetime import datetime, time, timedelta
from Modelos.biblioteca import Libro
from Modelos.element import Element, StockItem, UniqueItem
from Modelos.registro import Registro, RegistroBase
from Modelos.users import User, Profesor

class Servicio:
    def __init__(self, repositorio: Repositorio, usuarios: UserRepo):
        self.repositorio = repositorio
        self.usuarios = usuarios
    
    #Diccionario que retorna cada funcion del servicio segun el try-except
    #Estado(True-False), Mensaje(que es lo que se hizo), Data(devolver algo q me sirva al momento(id_element, etc))
    def res(self, estado: bool, mensaje: str, data: Any):
        return {
            "success": estado,
            "message": mensaje,
            "data": data
        }
    
    #considerar si esta funcion basta para la expiracion
    #lo q hace esta funcion es ver en q turno se encuentra el pedido y calcula su expiracion
    def calcularExpiracion(self, ahora):
        hora = ahora.time()
        fecha = ahora.date()
        turnos = [
            (time(7,40), time(11,50)),
            (time(13,10), time(17,30)),
            (time(17,40), time(21,30))
        ]

        for inicio, fin in turnos:
            if( inicio < hora < fin):
                return datetime.combine(fecha, fin)
            
    #Yo  recibiria de la api, en un json el id del element que se quiere prestar
    #Para solicitar una prestacion se necesiten las siguientes cosas:
    #El id_element del elemento que se quiere prestar, un objeto Usuario con o sin id dependiendo de si es la primera vez que pide
    #Un objeto registro.
    #Toda la estructura de objetos viene desde el frontened como json y 
    #luego en los Controller se transforman en los respectivos objetos usando pydantic

    #aca se pasa algo como ahora = datetime.now()
    #Esta funcion retorna lo q va en expiracion que puede ser 11:40, 17:20,21:30
    #Es decir el tiempo limite q se tiene para entregar
                   
    #yo debo de recibir del frontened, un usuario(alumno, profesor, etc) y un registro base
    #si el usuario viene sin id es pq no esta en la bd (hacer funcion para eso), entonces lo creo
    def prestar(self, usuario: User, registro_base: RegistroBase, expiracion=None):
        try:
            #esto me tiene que devolver Disponible, No disponible
            estado = self.repositorio.buscarEstado(registro_base.element_id)
            #pensar q retornar aca
            if (estado != "Disponible"):
                return self.res(False, "El elemento no esta disponible", None)
            
            if (usuario.id_usuario == None):
                usuario.id_usuario = self.usuarios.crearUsuario(usuario)         
            #acordarme de hacerle un alter table a la tabla esta de relacion para agreegarle la columna materia
            if isinstance(usuario, Profesor):
                if not (self.usuarios.buscarRelacionProfesorCurso(registro_base.destino, usuario.id_usuario)):
                    self.usuarios.vincularCursoProfesor(registro_base.destino ,usuario.id_usuario)

            elemento = self.repositorio.buscarElemento(registro_base.element_id)
            cantidad = registro_base.cantidad
            ahora = datetime.now()
            fecha = ahora.date()
            hora = ahora.time()

            if expiracion is None:
                expiracion = self.calcularExpiracion(ahora)
                if expiracion is None:
                    return (self.res(False, "No se puede realizar pedido, fuera de horario", None))
            #si es un stock y es reusable el estado es En curso
            #pero si es un elemento q no es reusable(osea q es descartable), nunca voy a tener q esperar a que se devuelva
            #directamente lo marco como consumido
            #lo mismo aplica para su expiracion, es un registro q nace "expirado" pq nunca se debe devolver
            if isinstance(elemento, StockItem) and elemento.isReusable:
                estado = "En curso"
            
            elif isinstance(elemento, StockItem):
                estado = "Consumido"
                expiracion = None
            else:
                estado = "En curso"

            nRegistro = Registro(
                element_id=registro_base.element_id,
                cantidad=cantidad,
                destino=registro_base.destino,
                usuario_id=usuario.id_usuario,
                fecha=fecha,
                hora=hora,
                expiracion=expiracion,
                estado=estado
            )

            self.repositorio.crearRegistro(nRegistro)
            #Si es un stockitem le tengo q restar las cantidades q estan en uso, y actualizar los disponibles
            #ver funcion en el repo
            #si es un uniqueitem directamente pasa aestar No disponible(pq esta en uso)
            if isinstance(elemento, StockItem):
                self.repositorio.actDisponibles(registro_base.element_id, cantidad)
            else:
                self.repositorio.actEstado(registro_base.element_id, "No disponible")
            return self.res(True, "Registro creado", None)
        except Exception as e:
            return self.res(False, f"Error al crear registro: {str(e)}", None)

    #Pensar en cmo extender esto
    #-se me ocurre verificar cosas como el horario en que se entrega(que sea el correcto)
    #- sera importante ver la hora de devolucion? 
    def devolver(self, registro_id):
        try:
            registro = self.repositorio.buscarRegistro(registro_id)
            if (registro.estado=="Terminado"):
                return self.res(False, f"Este registro ya habia terminado", None)
            elemento = self.repositorio.buscarElemento(registro.element_id)
            if isinstance(elemento, StockItem):
                self.repositorio.actDsp(registro.cantidad)
            self.repositorio.actEstado(elemento.id_element,"Disponible")
            self.repositorio.devolver(registro_id)
            return self.res(True, f"Se devolvio un elemento", None)
        except Exception as e:
            return self.res(False, f"Error al devolver elemento: {str(e)}", None)
        
    def crearElement(self, elemento: Element):
        try:
            id_element = self.repositorio.crearElement(elemento)
            return self.res(True, "Registro creado exitosamente", id_element)
        except Exception as e:
            return self.res(False, f"Error al crear el elemento: {str(e)}", None)

    def buscarElemento(self, id_element):
        try:
            elemento = self.repositorio.buscarElemento(id_element)
            return self.res(True, f"Objeto con id {id_element} encontrado", elemento)
        except Exception as e:
            return self.res(False, f"Error al buscar el elemento: {str(e)}", None)

    def borrar(self, id_element):
        try:
            if(self.repositorio.borrar(id_element)):
                return self.res(True, f"{id_element} borrado exitosamente", None)
            else:
                return self.res(False, f"{id_element} no encontrado", None)
        except Exception as e:
            return self.res(False, f"Error al eliminar el elemento: {str(e)}", None)
    
    def cargarNuevosElementos(self, id_element, pCantidad):
        try:
            self.repositorio.cargarNuevosElementos(pCantidad, id_element)
            self.repositorio.actEstado("Disponible")
            return self.res(True, f"Se ha actualizado la cantidad del objeto  con id {id_element}", None)
        except Exception as e:
            return self.res(False, f"Error al actualizar cantidad: {str(e)}", None)
        
    def actElemento(self, id_element, campo, nvalor):
        try:
            self.repositorio.actElemento(id_element, campo, nvalor)
            return self.res(True, f"Elemento con id {id_element} actualizado", None)
        except Exception as e:
            return False

    def verInventarioAll(self):
        res = self.repositorio.verInventarioAll()
        return res
    
    def verRegistros(self):
        res = self.repositorio.verRegistros()
        ls = []
        for registro in res:
            id_user = registro.usuario_id
            usuario = self.usuarios.buscarUsuario(id_user)
            nombre = usuario.nombre
            apellido = usuario.apellido
            elemento = self.repositorio.buscarElemento(registro.element_id)
            nelemento = elemento.nombre
            reg = registro.model_dump()
            reg["nombre"]=nombre
            reg["apellido"]=apellido
            reg["elemento_nombre"]=nelemento

            ls.append(reg)

        return ls
    
    
    
    