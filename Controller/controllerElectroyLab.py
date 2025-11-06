from fastapi import FastAPI
from Servicio.serviceElectroyLab import Service
from typing import Union
from fastapi import FastAPI, HTTPException
from Modelos.registro import RegistroBase
from Modelos.users import User
#ver como se hace un prefix en fastapi
#200 ok
#201 creado
#400 Bad request(dato invalido)
#404 not found
#401 Unauthorized
#500 Internal error
class controller():
    def __init__(self, service: Service,prefix):
        self.service = service 
        self.prefix = prefix
    def rutas(self, app: FastAPI):
        prefix = self.prefix
        @app.get(f'{prefix}/invenario')
        def verElementos():
            try:
                elementos = self.service.ver_elementos()
                return elementos
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'error al mostar elementos: {e}')
        @app.get(f'{prefix}/verElemento/{{id_elemento}}')
        def verElemento(id_elemento):
            try:
                elemento = self.service.ver_elemento(id_elemento)
                if(elemento["succes"]):
                    return elemento
                else:
                    raise HTTPException(status_code=404,detail=elemento["mensaje"])
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'error al mostar elemento: {str(e)}')
        @app.post(f'{prefix}/crearElemento')
        def crearElemento(elemento):
            try:
                Elemento = self.service.crear_elemento(elemento)
                if Elemento["succes"]:
                    return Elemento
                else:
                    raise HTTPException(status_code=404, detail=Elemento["mensaje"])
            except Exception as e:
                raise HTTPException(status_code=500,detail= f'error en la api al cargar un nuevo elemento: {e}')
        @app.delete(f'{prefix}/eliminarElemento/{{id_elemento}}')
        def eliminarElemento(id_elemento):
            try:
                elemento = self.service.eliminar_elemento(id_elemento)
                if (elemento["succes"]):
                    return elemento
                else:
                    raise HTTPException(status_code=404,detail=elemento["mensaje"])
            except Exception as e:
                raise HTTPException(status_code=500,detail= f'error en la api al elimina un elmento')
        @app.post(f'{prefix}/crearRegistro')
        def crearRegistro(data:RegistroBase, dataUsuario: User):
            try:
                registro = self.service.crear_registro(data,dataUsuario)
                return registro
            except Exception as e:
                raise HTTPException(status_code=500, detail= f'error en la api al crear un registro')
        @app.put(f'{prefix}/devolucion/{{id_registro}}')
        def devolucionDePedido(id_registro):
            try:
                self.service.devoluciones(self,id_registro)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'error en la api al devolver un elemento')
        @app.get(f'{prefix}/verRegistros')
        def verRegistros():
            try:
                registros = self.service.ver_registros()
                if (registros["succes"]):
                    return registros
                else:
                    raise HTTPException(status_code=404,detail=registros["mensaje"])
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'error en la api al mostar registros: {str(e)}')