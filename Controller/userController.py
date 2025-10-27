from typing import List
from Servicio.userService import Userservice
from fastapi import FastAPI, HTTPException
from Servicio.pwdManager import LoginRequest
class userController:
    def __init__(self, servicio: Userservice, prefix):
        self.servicio = servicio
        self.prefix = prefix
    
    def rutas(self, app: FastAPI):
        prefix = self.prefix

        @app.get("/")
        def corriendose():
            return {"Mensaje": "Corriendose"}
        
        @app.get(f"{self.prefix}/users")
        def verUsuarios():
            try:
                res = self.servicio.verUsuarios()
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al cargar usuarios: {str(e)}")
            
        @app.get(f"{self.prefix}/personal")
        def verPersonal():
            try:
                res = self.servicio.verPersonal()
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al cargar personal: {str(e)}")
            
        @app.post(f"{self.prefix}/personal/crear")
        def crearPersonal( id_user, npassword, jerarquia, email, accesos: List[str]):
            try:
                res = self.servicio.crearJerarquia(id_user, npassword, jerarquia, email ,accesos)
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al crear el personal: {str(e)}")
            
        @app.put(f"{self.prefix}/personal/acjerarquia")
        def actJerarquia(id_user, jerarquia, accesos: List[str]):
            try:
                res =  self.servicio.actJerarquia(id_user, jerarquia, accesos)
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al actualizar personal: {str(e)}")
            
        @app.delete(f"{self.prefix}/personal/eliminar/{{id_user}}")
        def darBaja(id_user):
            try:
                res = self.servicio.bajaPersonal(id_user)
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al eliminar personal: {str(e)}")
            
        @app.post(f"{self.prefix}/login")
        def login(data: LoginRequest):
            try:
                res = self.servicio.login(data.email, data.password)
                return res   
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al logearse: {str(e)}")
        


        
