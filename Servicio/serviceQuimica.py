from Servicio.serviceElectroyLab import Service, RegistroService
from Repositorio.repoElectroyLab import RepoGeneral
from Repositorio.userRepo import UserRepo
class serviceQuimica(Service, RegistroService):
    def __init__(self, repo:RepoGeneral,Usuario:UserRepo ):
        Service.__init__(self,repo, Usuario)
        