from typing import Union
from fastapi import FastAPI, HTTPException
from Modelos.registro import RegistroBase
from Modelos.users import User
from Servicio.servicio import Servicio
from Modelos.element import Element, UniqueItem, StockItem
#ver como se hace un prefix en fastapi
#200 ok
#201 creado
#400 Bad request(dato invalido)
#404 not found
#401 Unauthorized
#500 Internal error
class Controller:
    def __init__(self, servicio: Servicio, prefix):
        self.servicio = servicio
        self.prefix = prefix

    def rutas(self, app: FastAPI):
        prefix = self.prefix
        @app.get("/")
        def corriendose():
            return {"Mensaje": "Corriendose"}
        
        @app.get(f"{self.prefix}/inventario")
        def verElementos():
            try:
                res = self.servicio.verInventarioAll()
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al cargar el inventario: {str(e)}")

        #Volver a revisar este endpoint
        @app.get(f"{self.prefix}/elemento/{{id_element}}")
        def verElemento(id_element):
           try:
                res = self.servicio.buscarElemento(id_element)
                #recordar que res es un diccionario succes:bool
                if res["success"]:
                    return res
                else:
                    raise HTTPException(status_code=404, detail=res["message"])

           except Exception as e:
               raise HTTPException(status_code=500, detail=f"Error al obtener elemento: {str(e)}")
        
        @app.post(f"{self.prefix}/nuevoitem")
        def crearElement(elemento: Union[UniqueItem, StockItem, Element]):
            try:
                res = self.servicio.crearElement(elemento)
                if res["success"]:
                    return res
                else:
                    raise HTTPException(status_code=404, detail=f"{res["message"]}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al cargar elemento: {str(e)}")
            
        @app.delete(f"{self.prefix}/elemento/{{id_element}}")
        def borrarElement(id_element):
            try:
                res = self.servicio.borrar(id_element, "inventario")
                if res["message"]:
                    return res
                else:
                    raise HTTPException(status_code=404, detail=f"{res["message"]}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al eliminar elemento: {str(e)}")

        @app.post(f"{self.prefix}/prestar")
        def prestar(usuario: User, registro_base: RegistroBase):
            try:
                res = self.servicio.prestar(usuario, registro_base)
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al prestar elemento: {str(e)}")
            
        @app.post(f"{self.prefix}/devolver/{{registro_id}}")
        def devolver(registro_id):
            try:
                res = self.servicio.devolver(registro_id)
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al prestar elemento: {str(e)}")
        
        @app.get(f"{self.prefix}/registros")
        def verRegistros():
            try:
                res = self.servicio.verRegistros()
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al cargar registros: {str(e)}")
        
            

            
    