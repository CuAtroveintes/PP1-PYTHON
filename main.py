from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, Field
from typing import Annotated, Optional

app = FastAPI(title="Juegos de Mesa - Práctico 3")


IdInt = Annotated[int, Field(gt=0, description="El ID debe ser un entero mayor a 0")]
NombreStr = Annotated[str, Field(min_length=3, max_length=50, description="El nombre del juego debe tener entre 3 y 50 caracteres")]
CooperativoBool = Annotated[bool, Field(default=False, description="Indica si el juego es cooperativo o competitivo")]


class JuegoBase(BaseModel):
    id: IdInt
    nombre: NombreStr
    cooperativo: CooperativoBool


class JuegoResponse(JuegoBase):
    pass


 
db = [
    {"id": 1, "nombre": "Catan", "cooperativo": False},
    {"id": 2, "nombre": "Pandemic", "cooperativo": True}
]


@app.get(
    "/juegos", 
    response_model=list[JuegoResponse],
    summary="Obtener todos los juegos de mesa"
)
def obtener_juegos(
    cooperativo: Annotated[Optional[bool], Query(description="Filtrar por tipo de juego (cooperativo/competitivo)")] = None
):
    if cooperativo is not None:
        return [juego for juego in db if juego["cooperativo"] == cooperativo]
    return db


@app.post(
    "/juegos", 
    response_model=JuegoResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo juego de mesa"
)
def crear_juego(juego: JuegoBase):
    for x in db:
        if x["id"] == juego.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"El juego con ID {juego.id} ya existe."
            )
            
    db.append(juego.model_dump())
    return juego


@app.put(
    "/juegos/{juego_id}", 
    response_model=JuegoResponse,
    responses={404: {"description": "Juego no encontrado"}},
    summary="Actualizar un juego de mesa existente"
)
def actualizar_juego(
    juego_id: Annotated[int, Path(gt=0, description="ID del juego a actualizar (mayor a 0)")], 
    juego_actualizado: JuegoBase
):
    for index, juego in enumerate(db):
        if juego["id"] == juego_id:
            db[index] = juego_actualizado.model_dump()
            return juego_actualizado
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Juego con ID {juego_id} no encontrado para actualizar."
    )


@app.delete(
    "/juegos/{juego_id}", 
    response_model=dict,  
    responses={404: {"description": "Juego no encontrado"}},
    summary="Eliminar un juego de mesa"
)
def eliminar_juego(
    juego_id: Annotated[int, Path(gt=0, description="ID del juego a eliminar (mayor a 0)")]
):
    for index, juego in enumerate(db):
        if juego["id"] == juego_id:
            del db[index]
            return {"message": f"Juego con ID {juego_id} eliminado con éxito"}
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Juego con ID {juego_id} no encontrado para eliminar."
    )
