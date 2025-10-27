from typing import Any, List
from Conexiones.conexion import Conexion
from Modelos.users import User, Alumno, Profesor, Personal
from Repositorio.userRepo  import UserRepo
from Servicio.pwdManager import PasswordManager
from Servicio.tokenManager import TokenManager
class Userservice:
    def __init__(self, conexion: Conexion, repo: UserRepo, pm: PasswordManager, tm: TokenManager):
        self.conexion = conexion
        self.repo = repo
        self.pm = pm
        self.tm = tm

    def res(self, estado: bool, mensaje: str, data: Any):
        return {
            "success": estado,
            "message": mensaje,
            "data": data
        }


    #Atento aca, validar intentos de ingreso de sesion
    #Crear Tokens Managers
    def login(self, email, password):
        try:
            usuario = self.repo.usuario_email(email)
            accesos = self.repo.verAccesos(usuario.id_usuario)
            if not usuario:
                return self.res(False, "Email o contraseña incorrectos", None)
            
            if not self.pm.verify_pwd(password, usuario.password):
                return self.res(False, "Email o contraseña incorrectos", None)
            
            token_response= self.tm.tokenResponse(usuario.id_usuario, usuario.email, usuario.rol, usuario.zonas_acceso)
            return self.res(True, "Acceso", token_response.model_dump())
        except Exception as e:
            raise e
    
    #token str no Objeto Token
    def validarUsuario(self, token:str):
        res = self.tm.validarToken(token)
        if res:
            return self.res(True, "Validado", res)

        else:
            return self.res(res.succes, f"{res.message}", None)

    def crearUsuario(self, usuario: User):
        try:
            if isinstance(usuario, Personal):
                usuario.password = self.pm.hash_password(usuario.password)
                id = self.repo.crearUsuario(usuario)
            else:
                id = self.repo.crearUsuario(usuario)
            
            return (self.res(True, f"Usuario creado exitosamente", id ))

        except Exception as e:
            self.conexion.rollback()
            return (self.res(False, f"Error al crear usuario error: {str(e)}", None))

    def crearJerarquia(self, id_user, npassword, jerarquia, email, accesos: List[str]):
        jerarquias = ["Directivo", "Pasante", "Administrador"]
        try:
            if(jerarquia.capitalize() in jerarquias):
                n = self.pm.hash_pwd(npassword)
                self.repo.crearJerarquia(id_user, jerarquia, n, email)
                self.repo.asignarAcceso(id_user, accesos)
                return (self.res(True, f"Usuario ascendido a jerarquia {jerarquia}", None))
            else:
                return(self.res(False, f"Jerarquia {jerarquia} inexistente", None))
        
        except Exception as e:
            self.conexion.rollback()
            return (self.res(False, f"Error al crear usuario error: {str(e)}", None))

    def actJerarquia(self, id_user, jerarquia, accesos: List[str]):
        jerarquias = ["Directivo", "Pasante", "Administrador", "Bibliotecario"]
        try:
            if(self.repo.esPersonal):
                self.repo.actJerarquia(id_user, jerarquia)
                self.repo.eliminarAccesos(id_user)
                self.repo.asignarAcceso(id_user,accesos)
                return (self.res(True, "Se ha actualizado la jerarquia del usuario", None))
            else:
                return (self.res(False, "No es un usuario personal, cree uno", None))
        except Exception as e:
            return (self.res(False, f"Error al ascende usuario a {jerarquia}: {str(e)}", None))
    
    def bajaPersonal(self, user_id):
        try:
            self.repo.eliminarAccesos(user_id)
            self.repo.bajaPersonal(user_id)
            return (self.res(True, f"Usuario fuera del personal", None))
        except Exception as e:
            return (self.res(False, f"Error al dar de baja al usuario: {str(e)}", None))
        
    def borrar_usuario(self, id_user):
        try:
            self.repo.borrar_usuario(id_user)
            return (self.res(True, f"Usuario borrado exitosamente", None))
        
        except Exception as e:
            self.conexion.rollback()
            return (self.res(False, f"Error al eliminar usuario error: {str(e)}", None))
    
    def agCurso_profesor(self, id_profesor, id_curso, materia):
        try:
            self.repo.vincularCursoProfesor(id_profesor, id_curso, materia)
            return(self.res(True, f"Profesor id {id_profesor} vinculado al curso con id {id_curso}", None))
        except Exception as e:
            self.conexion.rollback()
            return (self.res(False, f"Error al eliminar usuario error: {str(e)}", None))
        
    def verUsuarios(self):
        try:
            alumnos = self.repo.verAlumnos()
            profesores = self.repo.verProfesores()
            usuarios = alumnos + profesores
            return (self.res(True, f" ", usuarios))
        except Exception as e:
            return (self.res(False, f"Error al cargar alumnos: {str(e)}", None))
        
    def verProfesores(self):
        try:
            res = self.repo.verProfesores()
            return (self.res(True, f" ", res))
        except Exception as e:
            return (self.res(False, f"Error al cargar profesores: {str(e)}", None))
        
    def verPersonal(self):
        try:
            res = self.repo.verPersonal()
            return (self.res(True, f" ", res))
        except Exception as e:
            return (self.res(False, f"Error al cargar personal: {str(e)}", None))
        
    def verUsuarios(self):
        try:
            res = self.repo.verAlumnos()
            res1 = self.repo.verProfesores()
            res.extend(res1)
            return(self.res(True, f"Usuarios", res ))
        except Exception as e:
            return (self.res(False, f"Error al cargar personal: {str(e)}", None))
    
    
    