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

#UniqueItem es para los objetos unicos como las computadoras o herramientas
class UniqueItem(Element):
    pass

#El isReusable es para las cosas que son reusables (es bool) o no
#Es reusable una escofina, una sierra. No es reusable un clavo, los guantes descartables del laboratorio, etc
#Disponible es un int, cuantas cantidades quedan disponibles de esa cosa
class StockItem(Element):
    cantidad: int
    disponibles: int
    isReusable: bool
