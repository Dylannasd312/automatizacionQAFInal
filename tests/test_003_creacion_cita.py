
import os

from core.assertions import (
    assert_status,
    assert_json,
    assert_true
)

from utils.helpers import buscar_horario_disponible


def ejecutar(contexto):

    api = contexto["api"]

    cita = {
        "paciente_id": contexto["datos"]["paciente_id"],
        "medico_id": int(os.getenv("QA_MEDICO_ID")),
        "especialidad_id": int(os.getenv("QA_ESPECIALIDAD_ID")),
        "consultorio_id": int(os.getenv("QA_CONSULTORIO_ID")),
        **buscar_horario_disponible(api, int(os.getenv("QA_MEDICO_ID")), int(os.getenv("QA_ESPECIALIDAD_ID")), int(os.getenv("QA_CONSULTORIO_ID"))),
        "origen": "RECEPCION",
        "observaciones": "Cita generada por automatización QA"
    }

    response = api.post("citas", cita)

    assert_status(response, 201)

    data = assert_json(response)
    registro = data["data"]

    cita_id = registro.get("id")

    assert_true(
        cita_id is not None,
        "No se obtuvo el ID de la cita."
    )

    assert_true(
        registro.get("estado") == "POR_PAGAR",
        "La cita no se creó con estado POR_PAGAR."
    )

    assert_true(
        registro.get("paciente_id")
        == contexto["datos"]["paciente_id"],
        "La cita no pertenece al paciente registrado."
    )

    contexto["datos"]["cita_id"] = cita_id

    return f"Cita creada correctamente. ID: {cita_id}"
