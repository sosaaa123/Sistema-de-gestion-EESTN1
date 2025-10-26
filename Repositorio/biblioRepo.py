from Modelos import element
from Modelos.element import Element, StockItem, UniqueItem
from Repositorio.repositorio import Repositorio
from Conexiones.conexion import Conexion
from Modelos.biblioteca import Libro
from Modelos.registro import Registro
class BiblioRepo(Repositorio):
    def __init__(self, esquema, conexion: Conexion):
        super().__init__(esquema, conexion)
        
    #27/9   Ver si este metodo esta bien, se tendria q aplicar lo mismo desde los otros repositorios
    # (en caso de que tengan mas objetos ademas de uItem y sItem)
    #No lo puedo sobreescribir de otra forma
    def crearElement(self, elemento):
        try:   
            element_id = super().crearElement(elemento)
            if isinstance(elemento, Libro):
                self.cur.execute(f"""
                    INSERT INTO {self.esquema}.libros (inventario_id, codigo_interno, ISBN, autor, editorial, categoria, 
                    publicacion_year, impresion_year, pais)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                            element_id,
                            elemento.codigo_interno,
                            elemento.ISBN,
                            elemento.autor,
                            elemento.editorial,
                            elemento.categoria,
                            elemento.publicacion_year,
                            elemento.impresion_year,
                            elemento.pais
                        ))

                self.conexion.commit()
            return element_id
        
        except Exception as e:
            self.conexion.rollback()
            raise e
        


    def verLibros(self):
        self.cur.execute(f"""
        SELECT i.element_id, i.nombre, i.descripcion, i.estado, i.ubicacion, i.ubicacion_interna, i.tipo,
        l.codigo_interno, l.ISBN, l.autor, l.editorial, l.categoria, l.publicacion_year, l.impresion_year, l.pais
        FROM {self.esquema}.libros l
        JOIN {self.esquema}.inventario i ON l.inventario_id = i.element_id 
        """)

        registros = self.cur.fetchall() 
        libros = [] 
        
        for registro in registros: 
            nLibro = Libro( 
                    id_element=registro[0], 
                    nombre=registro[1], 
                    descripcion=registro[2], 
                    estado=registro[3], 
                    ubicacion=registro[4], 
                    ubicacion_interna=registro[5], 
                    tipo=registro[6],
                    codigo_interno=registro[7],
                    ISBN=registro[8],
                    autor=registro[9], 
                    editorial=registro[10],
                    categoria=registro[11], 
                    publicacion_year=registro[12], 
                    impresion_year=registro[13], 
                    pais=registro[14] )
            
            libros.append(nLibro)

        return libros
    
    
    def buscarLibro(self, libro_id):
        self.cur.execute(f"""
        SELECT i.element_id, i.nombre, i.descripcion, i.estado, i.ubicacion, i.ubicacion_interna, i.tipo,
        l.codigo_interno, l.ISBN, l.autor, l.editorial, l.categoria, l.publicacion_year, l.impresion_year, l.pais
        FROM {self.esquema}.libros l
        JOIN {self.esquema}.inventario i ON l.inventario_id = i.element_id
        WHERE i.element_id = (%s)         
        """, (libro_id,))

        res = self.cur.fetchone()
        nLibro = Libro( 
                    id_element=res[0], 
                    nombre=res[1], 
                    descripcion=res[2], 
                    estado=res[3], 
                    ubicacion=res[4], 
                    ubicacion_interna=res[5], 
                    codigo_interno=res[6],
                    tipo=res[7],
                    ISBN=res[8],
                    autor=res[9], 
                    editorial=res[10],
                    categoria=res[11], 
                    publicacion_year=res[12], 
                    impresion_year=res[13], 
                    pais=res[14] )
        
        return nLibro
    
    def buscarElemento(self, id_element):
        try:

            elemento = super().buscarElemento(id_element)
            if isinstance(elemento, UniqueItem):
                self.cur.execute(f"""
                SELECT isbn, autor, editorial, categoria, publicacion_year, impresion_year, pais 
                FROM {self.esquema}.libros
                WHERE inventario_id =(%s)
                """,(id_element,))

                res = self.cur.fetchone()

                if(res):
                    nlibro = Libro(
                        id_element=id_element, 
                            nombre=elemento.nombre, 
                            descripcion=elemento.descripcion, 
                            estado=elemento.estado, 
                            ubicacion=elemento.ubicacion, 
                            ubicacion_interna=elemento.ubicacion_interna, 
                            codigo_interno=elemento.codigo_interno,
                            tipo=elemento.tipo,
                            ISBN=res[0],
                            autor=res[1], 
                            editorial=res[2],
                            categoria=res[3], 
                            publicacion_year=res[4], 
                            impresion_year=res[5], 
                            pais=res[6] 
                    )
                    return nlibro
                else:
                    return elemento
            else:
                return elemento
        except Exception as e:
            self.conexion.rollback()
            raise e
        

        
        
        
        
    
    def actElemento(self, id_element, campo, nvalor):
        camposLibro = ["isbn", "autor", "editorial", "categoria", "publicacion_year", "impresion_year", "pais"]
        try:
            elemento = self.buscarElemento(id_element)
           
            if isinstance(elemento, Libro) and campo.lower() in camposLibro:
                self.cur.execute(f"""
                    UPDATE {self.esquema}.libros
                    SET {campo} = %s
                    WHERE inventario_id = %s
                """, (nvalor, id_element))
                self.conexion.commit()
            
            else:
                
                super().actElemento(id_element, campo, nvalor)

        except Exception as e:
            self.conexion.rollback()
            raise e