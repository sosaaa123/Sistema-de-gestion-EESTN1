from pydantic import BaseModel
from typing import Optional

#ubicacion interna es en que stand lo ponen, ubicacion es el area (biblioteca, pañol, laboratorio, etc)
#Estado: disponible, en uso, no disponible
class Element(BaseModel):
    id_element: Optional[int] = None
    nombre: str
    descripcion: str
    estado: str
    ubicacion: str
    ubicacion_interna: str
    
    #En tipo es conveniente poner el tipo de objeto q va a ser dependiendo de las bd y donde se este trabajando
    #27/9 Actualizado: voy a utilizar tipo para las herencias mas primarias del elemento(Uniqueitem o Stockitem)
    tipo: str

#UniqueItem es para los objetos unicos como las computadoras o herramientas
#Recordar q lo elementos unicos tienen su propio codigo interno de identacion(text)
#ver el caso de las computadoras, las zapatillas, etc
#Me sirve para identificar mas rapido las cosas, se diferencia de StockItem q solo tiene su id heredado de elemento,
#y no puede llegar a tener ningun id mas
class UniqueItem(Element):
    codigo_interno: Optional[str] = None
    pass

#El isReusable es para las cosas que son reusables (es bool) o no
#Es reusable una escofina, una sierra. No es reusable un clavo, los guantes descartables del laboratorio, etc
#Disponible es un int, cuantas cantidades quedan disponibles de esa cosa
class StockItem(Element):
    cantidad: int
    disponibles: int
    isReusable: bool
