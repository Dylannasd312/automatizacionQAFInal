import os

from core.assertions import assert_status

from utils.helpers import fecha_pasada


def ejecutar(contexto):

    api = contexto["api"]

    cita = {

        "paciente_id":
            contexto["datos"]["paciente_id"],

        "medico_id":
            int(os.getenv("QA_MEDICO_ID")),

        "especialidad_id":
            int(os.getenv("QA_ESPECIALIDAD_ID")),

        "consultorio_id":
            int(os.getenv("QA_CONSULTORIO_ID")),

        "fecha_cita":
            fecha_pasada(2),

        "hora_cita":
            "10:00:00",

        "origen":
            "RECEPCION",

        "observaciones":
            "Prueba de fecha inválida"
    }

    response = api.post(
        "citas",
        cita
    )

    assert_status(response, 422)

    return (
        "El backend rechazó correctamente "
        "la fecha anterior al día actual."
    )