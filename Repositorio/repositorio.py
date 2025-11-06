from Conexiones.conexion import Conexion
from Modelos.element import Element, StockItem, UniqueItem
from Modelos.registro import Registro

#30/9 Las funciones que me faltan son la de actualizar campo y testear todo este repo
#Me sirve para los metodos que comparten todos los repositorios
#Metodos como los selects quizas los hago aparte.

#Clase general de repositorio, las demas clases reposotioro heredan del el
#contiene los metodos q todos los repositorios tienen en genral
#considerar el hipermorfismos de los repositorios
#vease el caso de crearElement que puede instanciar elemento unicos o de stock pero en el caso de una bd como biblioteca
#se necesita la instancia del objeto LIbro  si o si

class Repositorio:
    def __init__(self, esquema, conexion: Conexion):
        self.conexion = conexion
        self.cur = self.conexion.cur()
        self.esquema = esquema

    #Ver como puedo implementar este  metodo en bibliotecaRepo(aplicar hipermorfismo)
    #biblioteca deberia ver hacer un if instance para Libro, buscar como realizarlo
    def crearElement(self, elemento: Element):
        try:
            nombre = elemento.nombre
            descripcion = elemento.descripcion
            estado = elemento.estado
            ubicacion = elemento.ubicacion
            ubicacion_interna = elemento.ubicacion_interna
            tipo = elemento.tipo

            self.cur.execute(f"""
            INSERT INTO {self.esquema}.inventario(nombre, descripcion, estado, ubicacion, ubicacion_interna, tipo)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING element_id
            """, (nombre, descripcion, estado, ubicacion, ubicacion_interna, tipo))

            #Me traigo el id para poder poner el objeto en su respectiva tabla
            element_id = self.cur.fetchone()[0]

            if isinstance(elemento, StockItem):
                cantidad = elemento.cantidad
                disponibles = elemento.disponibles
                isReusable = elemento.isReusable

                self.cur.execute(f"""
                INSERT INTO {self.esquema}.stockitems(inventario_id, cantidad, disponibles, isreusable)
                VALUES (%s, %s, %s, %s)
                """, (element_id, cantidad, disponibles, isReusable))

            else:  #UniqueItem
                if(elemento.codigo_interno):
                    self.cur.execute(f"""
                    INSERT INTO {self.esquema}.uniqueitems(inventario_id, codigo_interno)
                    VALUES (%s, %s)
                    """, (element_id, elemento.codigo_interno))
                else:
                    self.cur.execute(f"""
                    INSERT INTO {self.esquema}.uniqueitems(inventario_id)
                    VALUES(%s)
                    """,(element_id,))

            self.conexion.commit()
            return element_id

        except Exception as e:
            self.conexion.rollback()
            raise e


    #Nota: hago un metodo buscarElemento general, todos los elementos del sistema pueden ser
    def buscarElemento(self, element_id):
        #Necesito una funcion q me retorne el elemento q se esta solicitando
        #Tengo q hacer un Left Join
        #Hago un select de todas las tablas q me interesan(inventario, stockItem, uniqueItem (i,l,s,u))
        with self.conexion as cur:
            try:
                cur.execute(f"""
                SELECT i.*, s.*, u.*
                FROM {self.esquema}.inventario i
                LEFT JOIN {self.esquema}.stockitems s on s.inventario_id = i.element_id
                LEFT JOIN {self.esquema}.uniqueitems u on u.inventario_id = i.element_id
                WHERE i.element_id = (%s);
                """, (element_id,))

                res = cur.fetchone()

                
                nombre = res[1]
                descripcion = res[2]
                estado = res[3]
                ubicacion = res[4]
                ubicacion_interna = res[5]
                tipo = res[6]

                
                if(tipo =="Uniqueitem" or tipo == "UniqueItem"):
                    nUniqueitem= UniqueItem(
                    id_element=element_id,
                    nombre=nombre,
                    descripcion=descripcion,
                    estado=estado,
                    ubicacion=ubicacion,
                    ubicacion_interna=ubicacion_interna,
                    tipo=tipo,
                    codigo_interno=res[11],

                    )
                
                    return nUniqueitem
                
                elif(tipo=="Stockitem" or tipo =="StockItem"):
                    nStockitem = StockItem(
                    id_element=element_id,
                    nombre=nombre,
                    descripcion=descripcion,
                    estado=estado,
                    ubicacion=ubicacion,
                    ubicacion_interna=ubicacion_interna,
                    tipo=tipo,
                    cantidad=res[8],
                    disponibles=res[9],
                    isReusable= res[10]
                    )
                    
                    return nStockitem
                
            except Exception as e:
                    self.conexion.rollback()
                    raise e
        
    #Para borrar registros, elementos, etc (lo manejo bien en service)
    def borrar(self, id):
        try:
            if(self.buscarElemento(id)):
                self.cur.execute(f"DELETE FROM {self.esquema}.inventario WHERE element_id = (%s)", (id,))
                self.conexion.commit()
                return True
            else:
                return False
        except Exception as e:
            self.conexion.rollback()
            raise e
    
    #Funcion para actualizar el estado de cualquier elemento
    def actEstado(self, id_element, nEstado):
        try:
            self.cur.execute(f"""
            UPDATE {self.esquema}.inventario
            SET estado = (%s)
            WHERE element_id = (%s);             
            """, (nEstado, id_element))

            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise e

    def buscarEstado(self, id_element):
        try:
            self.cur.execute(f"""
            SELECT estado FROM {self.esquema}.inventario
            WHERE element_id = (%s)
            """, (id_element,))

            res = self.cur.fetchone()
            return res[0]

        except Exception as e:
            self.conexion.rollback()
            raise e
    
    
    #Funcion para actualizar cantidad y disponibles
    #Si el se trata de un objeto que no es reusable se descuenta la cantidad
    #Si se trata de un ojeto reusable solo se descuentan los disponibles
    #Me dejo esta fucncion solo para restar las cantidades(revisar metodo devolver), sino me voy a hacer un embole en el servicio
    def actDisponibles(self, id_element, pCantidad):
        try:
            self.cur.execute(f"""
            SELECT cantidad, disponibles, isreusable
            FROM {self.esquema}.stockitems
            WHERE inventario_id = (%s)
            """, (id_element,))

            res = self.cur.fetchone()
            cantidad = res[0]
            disponibles = res[1]
            #Booleano
            isReusable = res[2]

            if(isReusable):

                if(disponibles - pCantidad  >= 0 ):
                    disponibles = disponibles - pCantidad

                    self.cur.execute(f"""
                    UPDATE {self.esquema}.stockitems
                    SET disponibles = (%s)
                    WHERE inventario_id = (%s)
                    """, (disponibles, id_element))
                    
                    if((disponibles - pCantidad) == 0):
                        self.actEstado(id_element, "No disponible")
                else:
                    return False
            else:
                if((disponibles - pCantidad)  >= 0):
                    disponibles = disponibles - pCantidad
                    nCantidad = cantidad - pCantidad

                    self.cur.execute(f"""
                    UPDATE {self.esquema}.stockitems
                    SET disponibles = (%s)
                    WHERE inventario_id = (%s)
                    """, (disponibles, id_element))
                    
                    self.cur.execute(f"""
                    UPDATE {self.esquema}.stockitems
                    SET cantidad = (%s)
                    WHERE inventario_id = (%s)
                    """, (nCantidad, id_element))

                    if(disponibles == 0):
                        self.actEstado(id_element, "No disponible")

            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise e
    #Casi lo mismo q el anterior pero aca solo aplica "sumar" y lo uso en la func devolver
    def actDsp(self, id_element, cantidad_devuelta):
        try:
            self.cur.execute( f"""
            UPDATE {self.esquema}.stockitems
            SET disponibles = (%s)
            WHERE inventario_id = (%s)
            """, (cantidad_devuelta, id_element))

            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise e
        
    #Me tiene q llegar un int de cuantos nuevos se cargan
    def cargarNuevosElementos(self, cantidad, id_element):
        try:
            self.cur.execute(f"""
            UPDATE {self.esquema}.stockitems
            SET disponibles = disponibles + (%s)
            WHERE inventario_id = (%s)
            """, (cantidad, id_element))

            self.cur.execute(f"""
            UPDATE {self.esquema}.stockitems
            SET cantidad = cantidad + (%s)
            WHERE inventario_id = (%s)
            """, (cantidad, id_element))

            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise e
        

    #   Dejo varios metodos para poder traerme los registros
    #   Esto es me trae todo lo del invnteraio(sin las relaciones de demas lados)
    #   Ver que hacer aca en para luego implementarlo en biblioteca(ver caso con libros)
    def verInventarioAll(self):
        cur = self.conexion.cur()
        try:
            cur.execute(f"""
            SELECT element_id, nombre, descripcion, estado, ubicacion, ubicacion_interna, tipo FROM {self.esquema}.inventario;""")

            res = cur.fetchall()
            inventario = []
            
            for i in res:
                n = None
                if(i[6] == "UniqueItem" or i[6] == "Uniqueitem"):
                    cur.execute(f"""
                    SELECT codigo_interno
                    FROM {self.esquema}.uniqueitems
                    WHERE inventario_id = (%s);                      
                    """,(i[0],))
                    r = cur.fetchone()
                    n = UniqueItem(id_element=i[0],
                                nombre=i[1],
                                descripcion=i[2],
                                estado=i[3],
                                ubicacion=i[4],
                                ubicacion_interna=i[5],
                                tipo=i[6],
                                codigo_interno=r[0])
                elif(i[6] == "Stockitem" or i[6] == "StockItem"):
                    cur.execute(f"""
                    SELECT cantidad, disponibles, isreusable
                    FROM {self.esquema}.stockitems
                    WHERE inventario_id = (%s);                      
                    """, (i[0],))

                    r = cur.fetchone()
                    n = StockItem(id_element=i[0],
                                nombre=i[1],
                                descripcion=i[2],
                                estado=i[3],
                                ubicacion=i[4],
                                ubicacion_interna=i[5],
                                tipo=i[6],
                                cantidad=r[0],
                                disponibles=r[1],
                                isReusable=r[2])

                inventario.append(n)
            return inventario
        except Exception as e:
            raise e

    

        
    def crearRegistro(self, registro: Registro):
        cur = self.conexion.cur()
        try:
            cur.execute(f"""
            INSERT INTO {self.esquema}.registros(usuario_id, element_id, cantidad, fecha, hora, expiracion, estado, destino)
            VALUES (%s,%s,%s,%s,%s,%s,%s, %s);""", (
                registro.usuario_id,
                registro.element_id,
                registro.cantidad,
                registro.fecha,
                registro.hora,
                registro.expiracion,
                registro.estado,
                registro.destino

            ))

            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise e
        


    def verRegistros(self):
        with self.conexion.cur() as cur:
            try:
                cur.execute(f"""
                SELECT registro_id, usuario_id, element_id, cantidad, fecha, hora, expiracion, estado, destino 
                FROM {self.esquema}.registros""")
                res = cur.fetchall() 
                registros = []
                for i in res:
                    n = Registro(
                        registro_id=i[0],
                        usuario_id=i[1],
                        element_id=i[2],
                        cantidad=i[3],
                        fecha=i[4],
                        hora=i[5],
                        expiracion=i[6],
                        estado=i[7],
                        destino=i[8]
                    )
                    registros.append(n)
                
                return registros
            except Exception as e:
                raise e
        
    

        #Metodo para manejar la devolucion de prestamos
    def devolver(self, registro_id):
        #Terminado? Devuelto? no se me ocurre nada mas entendible
        try:
            self.cur.execute(f"""
            UPDATE {self.esquema}.registros
            SET estado = (%s)
            WHERE registro_id = (%s)
            """, ("Terminado", registro_id))

            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise e

    def buscarRegistro(self, registro_id):
        try:
            self.cur.execute(f"""
            SELECT registro_id, usuario_id, element_id, cantidad, fecha, hora, expiracion, estado, destino
            FROM {self.esquema}.registros
            WHERE registro_id = (%s)
            """, (registro_id,))
            res = self.cur.fetchone()
            registro=Registro(
                registro_id=res[0],
                element_id=res[2],
                cantidad=res[3],
                destino=res[8],
                usuario_id=res[1],
                fecha=res[4],
                hora=res[5],
                expiracion=res[6],
                estado=res[7])
            return registro
        except Exception as e:
            raise e


    #Funcion para retornar los pedidos en curso(o sin devolver)
    def enCurso(self):
        try:
            self.cur.execute("""SELECT """)
        except Exception as e:
            self.conexion.rollback()




    #Tengo un problema q es q dependiendo el atributo q se quiera cambiar
    #Varia la tabla en la q esta inventario > (stockitem, uniqueitem)
    def actElemento(self, id_element, campo, nvalor):
            try:
                elemento = self.buscarElemento(id_element)
                #hasattr se fija si el elemento tiene ese atributo
                if hasattr(elemento, campo):
                    if campo in ["nombre", "descripcion", "estado", "ubicacion", "ubicacion_interna", "tipo"]:
                        self.cur.execute(f"""
                            UPDATE {self.esquema}.inventario
                            SET {campo} = %s
                            WHERE element_id = %s
                        """, (nvalor, id_element))

                    elif isinstance(elemento, StockItem) and campo in ["cantidad", "disponibles", "isreusable"]:
                        self.cur.execute(f"""
                            UPDATE {self.esquema}.stockitems
                            SET {campo} = %s
                            WHERE inventario_id = %s
                        """, (nvalor, id_element))

                    elif isinstance(elemento, UniqueItem) and campo == "codigo_interno":
                        self.cur.execute(f"""
                            UPDATE {self.esquema}.uniqueitems
                            SET codigo_interno = %s
                            WHERE inventario_id = %s
                        """, (nvalor, id_element))

                    else:
                        raise ValueError(f"Campo {campo} no valido para el elemento")

                    self.conexion.commit()
                else:
                    raise AttributeError(f"El elemento no tiene el campo {campo}")

            except Exception as e:
                self.conexion.rollback()
                raise e


        
    
    






