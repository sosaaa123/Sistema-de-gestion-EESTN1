from Repositorio.repoElectroyLab import RepoGeneral
from Conexiones.conexion import Conexion
class electroRepo(RepoGeneral):
    def __init__(self,esquema,conexion:Conexion):
        super().__init__(esquema, conexion)
