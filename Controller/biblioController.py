from fastapi import FastAPI, HTTPException
from Controller.controller import Controller
from Modelos.biblioteca import Libro
from Servicio.servicio import Servicio

class BiblioController(Controller):
    def __init__(self, servicio: Servicio, prefix):
        super().__init__(servicio, prefix)
    
    def rutas(self, app: FastAPI):
        super().rutas(app)

        @app.get(f"{self.prefix}/libros")
        def libros():
            try:
                res = self.servicio.verLibros()
                return res
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al cargar libros: {str(e)}")
