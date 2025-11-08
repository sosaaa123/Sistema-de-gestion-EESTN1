from Servicio.serviceElectroyLab import Service
from Repositorio.repoElectroyLab import RepoGeneral
from Repositorio.userRepo import UserRepo
class serviceElectro(Service):
    def __init__(self, repo: RepoGeneral, Usuario:UserRepo ):
        super().__init__(repo,UserRepo)
        
        
