from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from api.estudiantes import router as estudiantes_router
from api.mediciones import router as mediciones_router
from database import SessionLocal


app = FastAPI()
dataset_estudiantes: list[list] = []


class Estudiante(BaseModel):
    id: int
    nombre: str
    edad: int
    programa: str


@app.get("/")
def read_root():
    return {"message": "Hola mundo"}


@app.post("/estudiantes")
def agregar_estudiante(estudiante: Estudiante):
    if buscar_posicion_por_id(estudiante.id) is not None:
        return {"error": "Ya existe un estudiante con ese id"}

    estudiante_como_lista = [
        estudiante.id,
        estudiante.nombre,
        estudiante.edad,
        estudiante.programa,
    ]
    dataset_estudiantes.append(estudiante_como_lista)

    print("Dataset de estudiantes:")
    for registro in dataset_estudiantes:
        print(registro)

    return {
        "message": "Estudiante agregado correctamente",
        "estudiante": estudiante_como_lista,
        "dataset": dataset_estudiantes,
    }


class EstudianteActualizacion(BaseModel):
    nombre: Optional[str] = None
    edad: Optional[int] = None
    programa: Optional[str] = None


def imprimir_dataset():
    print("Dataset de estudiantes:")
    for registro in dataset_estudiantes:
        print(registro)


def buscar_posicion_por_id(id_estudiante: int):
    for posicion, registro in enumerate(dataset_estudiantes):
        if registro[0] == id_estudiante:
            return posicion
    return None


@app.get("/estudiantes/{id}")
def consultar_estudiante(id: int):
    posicion = buscar_posicion_por_id(id)
    if posicion is None:
        return {"error": "Estudiante no encontrado"}

    return {"estudiante": dataset_estudiantes[posicion]}


@app.put("/estudiantes/{indice}")
def reemplazar_estudiante(indice: int, estudiante: Estudiante):
    if indice < 0 or indice >= len(dataset_estudiantes):
        return {"error": "El estudiante no existe"}

    posicion_id = buscar_posicion_por_id(estudiante.id)
    if posicion_id is not None and posicion_id != indice:
        return {"error": "Ya existe un estudiante con ese id"}

    dataset_estudiantes[indice] = [
        estudiante.id,
        estudiante.nombre,
        estudiante.edad,
        estudiante.programa,
    ]
    imprimir_dataset()

    return {
        "message": "Estudiante reemplazado correctamente",
        "estudiante": dataset_estudiantes[indice],
        "dataset": dataset_estudiantes,
    }


@app.patch("/estudiantes/{indice}")
def actualizar_estudiante_parcial(
    indice: int, estudiante: EstudianteActualizacion
):
    if indice < 0 or indice >= len(dataset_estudiantes):
        return {"error": "El estudiante no existe"}

    datos_actualizados = estudiante.model_dump(exclude_unset=True)
    campos = {"nombre": 1, "edad": 2, "programa": 3}

    for campo, valor in datos_actualizados.items():
        dataset_estudiantes[indice][campos[campo]] = valor

    imprimir_dataset()

    return {
        "message": "Estudiante actualizado correctamente",
        "estudiante": dataset_estudiantes[indice],
        "dataset": dataset_estudiantes,
    }


@app.delete("/estudiantes/{indice}")
def eliminar_estudiante(indice: int):
    if indice < 0 or indice >= len(dataset_estudiantes):
        return {"error": "El estudiante no existe"}

    estudiante_eliminado = dataset_estudiantes.pop(indice)
    imprimir_dataset()

    return {
        "message": "Estudiante eliminado correctamente",
        "estudiante": estudiante_eliminado,
        "dataset": dataset_estudiantes,
    }
