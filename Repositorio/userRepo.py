from typing import List
from Conexiones.conexion import Conexion
from Modelos.users import User, Alumno, Profesor, Personal

class UserRepo:
    def __init__(self, esquema ,conexion: Conexion):
        self.esquema = esquema
        self.conexion = conexion
        self.cur = self.conexion.cur()


    def verAlumnos(self):
        try:
            with self.conexion.cur() as cur: 
                cur.execute(f"""
                                SELECT u.id, u.nombre, u.apellido, a.curso, a.especialidad
                                FROM {self.esquema}.usuarios u
                                INNER JOIN {self.esquema}.alumnos a ON u.id = a.user_id
                                """)
                
                res = cur.fetchall()
                alumnos = []
                for r in res:
                    alumno=Alumno(id_usuario=r[0], 
                                nombre=r[1], 
                                apellido=r[2], 
                                curso=r[3], 
                                especialidad=r[4])
                    alumnos.append(alumno)
                return alumnos
        except Exception as e:
            
            raise e
    
    def buscarRelacionArea(self, ids_areas: List[str], cur):
        areas = []
        for id in ids_areas:
            cur.execute(f"""
            SELECT area FROM {self.esquema}.areas
            WHERE area_id = (%s)
            """, (id,))

            res = cur.fetchone()
            if res:
                areas.append(res[0])
        return areas

    
    def verPersonal(self):
        try:
            with self.conexion.cur() as cur: 
                cur.execute(f"""
                SELECT u.id, u.nombre, u.apellido, p.rol, p.email
                FROM {self.esquema}.usuarios u
                INNER JOIN {self.esquema}.personal p ON u.id = p.user_id
                """)

                res = cur.fetchall()
                personal = []
                for r in res:
                    cur.execute(f"""
                    SELECT area_id FROM {self.esquema}.usuario_area_relacion
                    WHERE user_id= (%s)""",(r[0],))
                    
                    resp = cur.fetchall()
                    ids_areas = []
                    for id in resp:
                        ids_areas.append(id[0])
                    
                    
                    areas = self.buscarRelacionArea(ids_areas, cur)

                    npersonal= Personal(
                        id_usuario=r[0],
                        nombre=r[1],
                        apellido=r[2],
                        rol=r[3],
                        email=r[4],
                        zonas_acceso=areas
                    )

                    personal.append(npersonal)
                
                self.conexion.commit() 
                return personal
        except Exception as e:
            self.conexion.rollback()
            raise e

    #Nota: aca lo iideal tambien seria devolver los cursos del profesor, para eso se debe cambiar el modelo de profesore
    #agregarles el atributo cursos como lista y demas. Ahora por paja y por tiempo lo dejo solo asi        
    def verProfesores(self):
        self.cur.execute(f"""
        SELECT u.id, u.nombre, u.apellido
        FROM {self.esquema}. usuarios u
        INNER JOIN {self.esquema}.profesores p ON u.id = p.user_id
        """)
        profesores = []
        res= self.cur.fetchall()
        for r in res:
            profesor = Profesor(id_usuario=r[0], nombre=r[1], apellido=r[2])
            profesores.append(profesor)
        return profesores

    
    def areas(self):
        self.cur.execute(f"""SELECT area_id, area FROM {self.esquema}.areas""")
        res = []

        for f in self.cur.fetchall():
            res.append({
                "area_id":f[0],
                "area":f[1]}
            )

        return res
    
    def bsarea_id(self, area_nombre):
        self.cur.execute(f"""
        SELECT area_id FROM {self.esquema}.areas
        WHERE area = (%s)
        """, (area_nombre,))

        res = self.cur.fetchone()
        if res is None:
            return None
        return res[0]


    #Funcion crear usuario q vale
    def crearUsuario(self, nUsuario):
        try:
            nombre = nUsuario.nombre
            apellido = nUsuario.apellido
            self.cur.execute(f"""
            INSERT INTO {self.esquema}.usuarios(nombre, apellido) 
            VALUES (%s, %s) 
            RETURNING id""", (nombre, apellido))
        
            user_id = self.cur.fetchone()[0]
            self.conexion.commit()
        
            if isinstance(nUsuario, Alumno):
                curso = nUsuario.curso
                especialidad = nUsuario.especialidad
                self.cur.execute(f"""
                INSERT INTO {self.esquema}.alumnos(user_id, curso, especialidad)
                VALUES (%s, %s, %s)
                """, (user_id, curso, especialidad))
                self.conexion.commit()

            elif isinstance(nUsuario, Profesor):
                self.cur.execute(f"""
                INSERT INTO {self.esquema}.profesores(user_id)
                VALUES (%s)""", (user_id,))
                self.conexion.commit()

            elif isinstance(nUsuario, Personal):
                self.cur.execute(f"""
                INSERT INTO {self.esquema}.personal(user_id, rol, password, email)
                VALUES (%s,%s,%s,%s)""", (user_id, nUsuario.rol, nUsuario.password, nUsuario.email))

                for zona in nUsuario.zonas_acceso:
                    r = self.bsarea_id(zona)
                    if (r != None):
                        self.cur.execute(f"""
                        INSERT INTO {self.esquema}.usuario_area_relacion(user_id, area_id)
                        VALUES (%s,%s)
                        """, (user_id, r))
                self.conexion.commit()
            return user_id
            
        except Exception as e:
            self.conexion.rollback()
            raise e
            

    def borrar_usuario(self, id_usuario):
        try:
            self.cur.execute(f"DELETE FROM {self.esquema}.usuarios WHERE id = (%s)", (id_usuario,))
            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise e


    
    
    def usuario_email(self, email):
        self.cur.execute(f"""
        SELECT u.id, u.nombre, u.apellido, p.rol, p.password, p.email
        FROM {self.esquema}.usuarios u
        INNER JOIN {self.esquema}.personal p ON u.id = p.user_id
        WHERE p.email = (%s)
        """, (email,))
        

        res = self.cur.fetchone()
        accesos = self.verAccesos(res[0])
        usuario = Personal(id_usuario=res[0], 
                           nombre=res[1], 
                           apellido=res[2], 
                           rol=res[3], 
                           password=res[4],
                           email=res[5],
                           zonas_acceso=accesos)
        return usuario

    
    def vincularCursoProfesor(self, curso_id, profesor_id, materia):
        try:
            self.cur.execute("""
            INSERT INTO profesores_cursos(profesor_id, curso_id, materia)
            VALUES (%s,%s, %s)
            """, (profesor_id, curso_id, materia))

            self.conexion.commit()

        except Exception as e:
            self.conexion.rollback()
            raise e

    #Funcion para actualizar la jerarquia del usuario(ej: de alumno a pasante(administrador))
    #Considerar que un usuario puede tener varias jerarquias
    #Pensar cual sera el superadministrador
    #Nota: un alumno puede pasar a profesor, tiene sentido ese pasaje en el sistema?

    #Dos metodos para actualizar jerarquia
    #at_jerarquia para los casos de: 
    #-Alumno a personal
    #-Profesor a personal
    #Pq necesitan necesaramente una contraseña de acceso



    def crearJerarquia(self, id_user, rol, npassword, email):
        #Roles: Directivo, pasante, administradoro
        #Pasante: pañolero/pañolera
        try: 
            
            self.cur.execute(f"""
            INSERT INTO {self.esquema}.personal(user_id, rol, password, email)
            VALUES (%s,%s,%s,%s)
            """, (id_user, rol.capitalize(), npassword, email))

            self.conexion.commit()

        except Exception as e:
            self.conexion.rollback()
            raise e
        
    def asignarAcceso(self, id_user, accesos: List[str]):
         
        for acceso in accesos:
            id = self.bsarea_id(acceso.capitalize())
            try:
                self.cur.execute(f"""
                INSERT INTO {self.esquema}.usuario_area_relacion(user_id, area_id)
                VALUES (%s,%s)
                """,(id_user, id))

                self.conexion.commit()
            except Exception as e:
                raise e

    
    #Este es mas general, funciona si el usuario ya esta creado
    #Actualizar jerarquia personal(ya tiene un usuario - contraseña creado)
    #Revisar metodo, no se puede ser Pasante y Directivo a la vez(consultar como reemplazar un campo)
    def actJerarquia(self, id_user, njerarquia):
        try:
            self.cur.execute(f"""
            UPDATE {self.esquema}.personal 
            SET rol = %s
            WHERE user_id = %s
            """, (njerarquia.capitalize(), id_user))
            
            self.conexion.commit()
            
        except Exception as e:
            self.conexion.rollback()
            raise e
        
    def esPersonal(self, id_user):
        try:
            self.cur.execute(f"""
            SELECT user_id FROM {self.esquema}.personal 
            WHERE user_id = %s
            """, (id_user,))
            
            if self.cur.fetchone() is not None:
                return True
            else:
                return False
            
        except Exception as e:
            raise e
    
    def verAccesos(self, id_user):
        self.cur.execute(f"""
        SELECT area_id FROM {self.esquema}.usuario_area_relacion
        WHERE user_id = (%s)
        """,(id_user,))

        res = self.cur.fetchall()
        accesos = []
        for r in res:
            self.cur.execute(f"""
            SELECT area FROM {self.esquema}.areas
            WHERE area_id = (%s)
            """,(r[0],))

            acceso = self.cur.fetchall()
            accesos.append(acceso[0][0])
        
        return accesos
    
    def eliminarAccesos(self, id_user):
        try:
            self.cur.execute(f"""
            DELETE FROM {self.esquema}.usuario_area_relacion 
            WHERE user_id = %s
            """, (id_user,))
            
            self.conexion.commit()
            
        except Exception as e:
            self.conexion.rollback()
            raise e
    
    #Ejemplo cuando un pasante termina el año se debe eliminar su usario de la tabla Personal(junto con sus accesos)
    def bajaPersonal(self, id_user):
        self.cur.execute(f"""
        DELETE FROM {self.esquema}.personal
        WHERE user_id = (%s)
        """,(id_user,))
    
    def buscarRelacionProfesorCurso(self, nombre_del_curso, profesor_id):

        self.cur.execute(f"""
        SELECT id FROM {self.esquema}.cursos
        WHERE nombre = (%s)
        """,(nombre_del_curso,))

        cursoId = self.cur.fetchone()
        cursoId = cursoId[0]


        self.cur.execute(f"""
        SELECT * FROM {self.esquema}.profesores_cursos
        WHERE profesor_id = (%s) 
            AND curso_id = (%s)
        """, (profesor_id, cursoId))

        x = self.cur.fetchone()
        if (x):
            return True
        else:
            return False

    def buscarUsuario(self, id_user):
        with self.conexion.cur() as cur:
            try:
                cur.execute(f"""
                SELECT id, nombre, apellido from {self.esquema}.usuarios
                WHERE id = (%s)
                """, (id_user,))

                res = cur.fetchone()

                usuario = User(id_usuario=res[0], nombre=res[1], apellido=res[2])
                return usuario
            except Exception as e:
                raise e

