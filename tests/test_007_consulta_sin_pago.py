
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
        "observaciones": "Cita sin pago para prueba QA"
    }

    respuesta_cita = api.post("citas", cita)

    assert_status(respuesta_cita, 201)

    cita_data = assert_json(respuesta_cita)

    cita_id = cita_data["data"]["id"]

    assert_true(
        cita_data["data"]["estado"] == "POR_PAGAR",
        "La cita de prueba no está POR_PAGAR."
    )

    consulta = {
        "cita_id": cita_id,
        "paciente_id": contexto["datos"]["paciente_id"],
        "medico_id": int(os.getenv("QA_MEDICO_ID")),
        "especialidad_id": int(os.getenv("QA_ESPECIALIDAD_ID")),
        "motivo_consulta": "Consulta de prueba sin pago",
        "enfermedad_actual": "Registro de prueba QA",
        "diagnostico": "Pendiente",
        "tratamiento": "Pendiente",
        "observaciones": "Debe rechazarse por falta de pago",
        "estado": "EN_CURSO"
    }

    response = api.post("consultas", consulta)

    assert_status(response, 422)

    data = assert_json(response)

    return (
        "Consulta rechazada correctamente: "
        + data.get("message", "")
    )
