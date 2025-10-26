from Repositorio.repositorio import Repositorio
from Repositorio.userRepo import UserRepo
from Servicio.servicio import Servicio

class BiblioService(Servicio):
    def __init__(self, repositorio: Repositorio, usuarios: UserRepo):
        super().__init__(repositorio, usuarios)

    def verLibros(self):
       try:
        return self.repositorio.verLibros()
       except Exception as e:
          return self.res(False, f"Error al cargar libros {str(e)}, None")