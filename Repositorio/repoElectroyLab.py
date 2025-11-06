from Conexiones.conexion import Conexion
from Modelos.element import UniqueItem, StockItem, Element
from Modelos.registro import Registro, RegistroBase
class RepoGeneral():
    def __init__(self, esquema,conexion : Conexion):
        self.conexion = conexion
        self.esquema = esquema
    def crear(self):
        try:
            with self.conexion.cur() as cur:
                cur.execute(f'CREATE TABLE IF NOT EXISTS {self.esquema}.inventario(id_elemento SERIAL PRIMARY KEY, tipo TEXT)')
        except Exception as e:
            raise ValueError(f'error: {e}')
    def crear_tabla_inventario(self):
        try:
            with self.conexion.cur() as cur:
               
                cur.execute(f'CREATE TABLE IF NOT EXISTS {self.esquema}.inventario_stock (id_elemento INTEGER NOT NULL, FOREIGN KEY (id_elemento) REFERENCES {self.esquema}.inventario(id_elemento) , nombre TEXT, descripcion TEXT, estado TEXT, ubicacion TEXT, ubicacion_interna TEXT, tipo TEXT , cantidad  INTEGER, disponibles INTEGER, reusable BOOLEAN)')
                cur.execute(f'CREATE TABLE IF NOT EXISTS {self.esquema}.inventario_unicos (id_elemento INTEGER NOT NULL,FOREIGN KEY (id_elemento) REFERENCES {self.esquema}.inventario(id_elemento) ,nombre TEXT,  descripcion TEXT, estado TEXT, ubicacion TEXT, ubicacion_interna TEXT, tipo TEXT, codigo_interno TEXT)')
                self.conexion.commit()
        except Exception as e:
                self.conexion.rollback()
                raise RuntimeError(f"hubo un error al crear la tabla: {e}")
    def crear_elemento(self, data):
        try:
            with self.conexion.cur() as cur:
                
                cur.execute(f'INSERT INTO {self.esquema}.inventario (id_elemento, tipo) VALUES(DEFAULT, %s) RETURNING id_elemento',(data.tipo,))
                id_element = cur.fetchone()[0]
                data.id_element = id_element
                datadic = vars(data)
                if isinstance(data, StockItem):
                    cur.execute(f"INSERT INTO {self.esquema}.inventario_stock(id_elemento ,nombre, descripcion, estado, ubicacion, ubicacion_interna ,tipo,cantidad,disponibles, reusable) VALUES (%(id_element)s,%(nombre)s, %(descripcion)s,%(estado)s,%(ubicacion)s,%(ubicacion_interna)s,%(tipo)s,%(cantidad)s,%(disponibles)s,%(isReusable)s)",datadic)
                    self.conexion.commit()
                elif isinstance(data, UniqueItem):
                    cur.execute(f"INSERT INTO {self.esquema}.inventario_unicos (id_elemento,nombre, descripcion, estado, ubicacion, ubicacion_interna ,tipo,codigo_interno) VALUES (%(id_element)s,%(nombre)s, %(descripcion)s,%(estado)s,%(ubicacion)s,%(ubicacion_interna)s,%(tipo)s,%(codigo_interno)s)",datadic)
                    self.conexion.commit()
                else:
                    raise ValueError("no cumple ninguna tipo")
        except Exception as e:
                self.conexion.rollback()
                raise RuntimeError(f"hubo un error en la base de datos herramientas_inventario al crear una nueva herramienta: {e}")
    def ver_inventario(self):
            try:
                with self.conexion.cur() as cur:
                    lista_elementos = []
                    cur.execute(f'''  SELECT i.id_elemento, s.nombre, s.descripcion, s.estado, s.ubicacion, s.ubicacion_interna,
                           s.tipo, s.cantidad, s.disponibles, s.reusable, NULL AS codigo_interno
                    FROM {self.esquema}.inventario i
                    JOIN {self.esquema}.inventario_stock s ON s.id_elemento = i.id_elemento

                    UNION ALL

                    SELECT i.id_elemento, u.nombre, u.descripcion, u.estado, u.ubicacion, u.ubicacion_interna,
                           u.tipo, NULL AS cantidad, NULL AS disponibles, NULL AS reusable, u.codigo_interno
                    FROM {self.esquema}.inventario i
                    JOIN {self.esquema}.inventario_unicos u ON u.id_elemento = i.id_elemento''')
                    inventario = cur.fetchall()
                    for elementos in inventario:
                        id_elemento, nombre, descripcion, estado, ubicacion,ubicacion_interna, tipo, cantidad, disponibles,isreusable, codigo_interno = elementos
                        if (tipo == "stock"):
                            elemento = StockItem(
                                id_element= id_elemento,
                                nombre=nombre,
                                descripcion=descripcion,
                                estado=estado,
                                ubicacion=ubicacion,
                                ubicacion_interna=ubicacion_interna,
                                tipo=tipo,
                                cantidad=cantidad,
                                disponibles=disponibles,
                                isReusable=isreusable
                            )
                            lista_elementos.append(elemento)
                        elif(tipo== "unico"):
                            elemento = UniqueItem(
                                id_element= id_elemento,
                                nombre=nombre,
                                descripcion=descripcion,
                                estado=estado,
                                ubicacion=ubicacion,
                                ubicacion_interna=ubicacion_interna,
                                tipo=tipo,
                                codigo_interno=codigo_interno
                            )
                            lista_elementos.append(elemento)
                    return lista_elementos    
            except Exception as e:
                raise RuntimeError (f"hubo un error en la base de datos al querer recuperar las herramientas: {e}")
    def ver_elemento(self, identificador):
        try: 
            with self.conexion.cur() as cur:
                cur.execute(f'SELECT tipo FROM {self.esquema}.inventario WHERE id_elemento = %s', (identificador,))
                tipo = cur.fetchone()[0]
                if (tipo == "stock"):
                    cur.execute(f'SELECT * FROM {self.esquema}.inventario_stock WHERE id_elemento = %s ',(identificador,))
                    elemento = cur.fetchone()
                    if elemento is None:
                        return None
                    elemento_stock = StockItem( 
                        id_element=elemento[0], 
                        nombre=elemento[1], 
                        descripcion=elemento[2], 
                        estado=elemento[3], 
                        ubicacion=elemento[4], 
                        ubicacion_interna=elemento[5],  
                        tipo=elemento[6],
                        cantidad= elemento[7],
                        disponibles = elemento[8],
                        isReusable=elemento[9]
                            )
                    return elemento_stock

                elif(tipo == "unico"):
                    cur.execute(f'SELECT * FROM {self.esquema}.inventario_unicos WHERE id_elemento = %s',(identificador,))
                    elemento = cur.fetchone()
                    if elemento is None:
                        return None
                    elemento_unicos = UniqueItem( 
                        id_element=elemento[0], 
                        nombre=elemento[1], 
                        descripcion=elemento[2], 
                        estado=elemento[3], 
                        ubicacion=elemento[4], 
                        ubicacion_interna=elemento[5],  
                        tipo=elemento[6],
                        codigo_interno = elemento[7]
                            )
                    return elemento_unicos
                else:
                    raise ValueError("no existe elemento con ese id")
        except Exception as e:
            raise RuntimeError(f"hubo un error en la base de datos al querer recuperar una elemento: {e}")
    def actualizar_disponibles(self,id_elemento:int, nCantidad: int):
        try:
            with self.conexion.cur() as cur:
                cur.execute(f"UPDATE {self.esquema}.inventario_stock SET disponibles = %s WHERE id_elemento = %s",(nCantidad, id_elemento))
                self.conexion.commit()
        except Exception as e:
             raise RuntimeError(f"hubo un error en la base de datos al actualizar la cantidad: {e}")
    def actualizar_estado_id(self,id_elemento : int, nEstado: str, tipo):
        try:
            with self.conexion.cur() as cur:
                if (tipo == "stock"):
                    cur.execute(f"UPDATE {self.esquema}.inventario_stock SET estado = %s WHERE id_elemento = %s",(nEstado, id_elemento))
                    self.conexion.commit()
                elif(tipo == "unico"):
                    cur.execute(f"UPDATE {self.esquema}.inventario_unicos SET estado = %s WHERE id_elemento = %s" ,(nEstado, id_elemento))
                    self.conexion.commit()
                else:
                    raise ValueError("no hay elementos con ese id")
        except Exception as e:
            self.conexion.rollback()
            raise RuntimeError(f"error al alctualizar estado en la tabla inventario_stock: {e}")
    def eliminar_elemento(self,id_elemento:int,tipo):
        try:
            with self.conexion.cur() as cur:
                if (tipo== "stock"):
                    cur.execute(f"DELETE FROM {self.esquema}.inventario_stock WHERE id_elemento = %s",(id_elemento,))
                    self.conexion.commit()
                elif (tipo == "unico"):
                    cur.execute(f"DELETE FROM {self.esquema}.inventario_unicos WHERE id_elemento = %s",(id_elemento,))
                    self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise ValueError(f"error al eliminar una herramienta: {e}")
    def crear_tabla_registro(self):
        try:
            with self.conexion.cur() as cur:
                cur.execute(f'CREATE TABLE {self.esquema}.registro (id_registro SERIAL PRIMARY KEY,id_elemento INTEGER NOT NULL ,FOREIGN KEY (id_elemento) REFERENCES {self.esquema}.inventario(id_elemento),usuario_id INTEGER NOT NULL,FOREIGN KEY (usuario_id) REFERENCES usuarios.usuarios (id),cantidad INTEGER,fecha TEXT, hora TEXT,expiracion TEXT,esatdo TEXT, destino TEXT )')
        except Exception as e:
            raise RuntimeError(f'error al crear tabla: {e}')
    def crear_registro(self, data:dict):
        try:
            with self.conexion.cur() as cur:
                cur.execute(f"INSERT INTO {self.esquema}.registro (id_elemento,usuario_id,cantidad, fecha, hora,expiracion, estado, destino ) VALUES (%(element_id)s, %(usuario_id)s,%(cantidad)s,%(fecha)s,%(hora)s,%(expiracion)s, %(estado)s,%(destino)s)",data)
                self.conexion.commit()
        except Exception as e:
            raise RuntimeError(f"error al crear un registro")
    def actualizar_estado_registro(self, id_registro, nEstado):
        try:
            with self.conexion.cur() as cur:
                cur.execute(f"UPDATE {self.esquema}.registro SET estado = %s WHERE id_registro = %s",(nEstado,id_registro,))
                self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise RuntimeError(f"error al alctualizar estado en la tabla de registro: {e}")
    def ver_registros(self): 
        try:
            with self.conexion.cur() as cur:
                cur.execute(f"SELECT * FROM {self.esquema}.registro")
                registros = cur.fetchall()
                if registros is None:
                    return None
                lista_de_registro=[]
                for registro in registros:
                    registro_herramienta = Registro(
                        registro_id= registro[0],
                        element_id= registro[1],
                        cantidad=registro[2],
                        destino= registro[3],
                        usuario_id=registro[4],
                        fecha=registro[5],
                        hora= registro[6],
                        expiracion= registro[7],
                        estado= registro[8],
                    )
                    lista_de_registro.append(registro_herramienta)
                return lista_de_registro
        except Exception as e:
            raise RuntimeError(f"error al traer la los datos de registros: {e}")
    def ver_registro(self, id_registro):
        try:
            with self.conexion.cur() as cur:
                cur.execute(f'SELECT * FROM {self.esquema}.registro WHERE id_registro = %s',(id_registro,))
                registro = cur.fetchone()
                if registro is None:
                    return None
                else:
                    registro1 = Registro(
                        registro_id= registro[0],
                        element_id= registro[1],
                        cantidad=registro[2],
                        destino= registro[3],
                        usuario_id=registro[4],
                        fecha=registro[5],
                        hora= registro[6],
                        expiracion= registro[7],
                        estado= registro[8],
                    )
                    return registro1
        except Exception as e:
            raise ValueError(f'error al traer un registro: {e}')
                