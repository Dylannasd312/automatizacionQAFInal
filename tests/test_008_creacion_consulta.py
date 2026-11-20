import os

from core.assertions import (
    assert_status,
    assert_json,
    assert_true
)


def ejecutar(contexto):

    api = contexto["api"]

    consulta = {

        "cita_id":
            contexto["datos"]["cita_id"],

        "paciente_id":
            contexto["datos"]["paciente_id"],

        "medico_id":
            int(os.getenv("QA_MEDICO_ID")),

        "especialidad_id":
            int(os.getenv("QA_ESPECIALIDAD_ID")),

        "motivo_consulta":
            "Consulta respiratoria de prueba",

        "enfermedad_actual":
            "Registro ficticio para automatización",

        "diagnostico":
            "Pendiente de evaluación médica",

        "tratamiento":
            "Pendiente de indicación médica",

        "observaciones":
            "Consulta generada mediante Python",

        "estado":
            "EN_CURSO"
    }

    response = api.post(
        "consultas",
        consulta
    )

    assert_status(response, 201)

    data = assert_json(response)

    registro = data["data"]

    consulta_id = registro.get("id")

    assert_true(
        consulta_id is not None,
        "No se obtuvo el ID de la consulta."
    )

    assert_true(
        registro.get("estado") == "EN_CURSO",
        "La consulta no está EN_CURSO."
    )

    contexto["datos"]["consulta_id"] = consulta_id

    cita_response = api.get(
        f"citas/{contexto['datos']['cita_id']}"
    )

    assert_status(cita_response, 200)

    cita_data = assert_json(cita_response)

    assert_true(
        cita_data.get("estado") == "EN_CONSULTA",
        "La cita no cambió al estado EN_CONSULTA."
    )

    return f"Consulta creada correctamente. ID: {consulta_id}"