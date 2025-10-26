from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime, time
#Cada cosa que se preste va a saltar como registro. Si queremos ver que cosas se sacaron al mismo tiempo por una persona hacemos un join
#Estado es para saber si ya se entregaron o no(capazbuscar otro nombre mas especifico)

#Expiracion: las cosas del pañol tendrian que tener de expiracion el tiempo que falte para que se cierren los
#pañoles o y la biblioteca (entregar antes de las 21:30, 17:20) 


#ver si se puede agregar un atributo "Destino" que diga hacia donde va,
#en el caso del alumno es facil identificar el destino(tiene un atributo curso)
#pero en el caso de un profesor es una relacion de uno a muchos cursos

#clase abstracta
#11/9 Agrego id a todas las clases, les pongo 
#12/9 Cambie todas las clases a pydantic
#Registro_id optional[int] = None me permite a veces poder armar objetos con el id a veces no
#fijarse el repositorio de usuarios cuando debo crear un usuario, no puedo pasarle como parametro un id, ya que el id lo define la BD
#al reves pasa cuando me quiero traer todos los uasuarios y pasarlo a un array de objeto, tengo que q traerme los id y ponerlos si o si

#El campo estado solo puede ser 3 cosas: Devuelto, en curso y consumido.
#Consumido es para aquellos objetos Stock que tienen True en is_reusable, 
#esto se sobreescribe en la capa de servicio if isReusable = True, registro_estado = consumido.

#13/9, agrego una herencia mas a Registro
#Entiendase que RegistroBase es lo q se recibe del frontened, es el "pedido"
#El registro que va cargado en la bd es Registro y se completan sus atributos(fecha, hora, etc) en la capa de servicio

#3/10 vuelvo a pasar registro_id al base pq no me gusta que id sea q atributo de un registro idk
class RegistroBase(BaseModel):
    registro_id: Optional[int] = None
    element_id: int
    cantidad: int
    destino: str

class Registro(RegistroBase):
    usuario_id: int
    fecha: date
    hora: time
    expiracion: Optional[datetime]
    estado: str

