from Repositorio.repositorio import Repositorio
from Conexiones.conexion import Conexion

#Va a quedar re pelado este repo, no  se me ocurre q mas agregarle q no tenga el general
class PrgRepo(Repositorio):
    def __init__(self, esquema, conexion: Conexion):
        super().__init__(esquema)
