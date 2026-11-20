from core.assertions import (
    assert_status,
    assert_json
)


def ejecutar(contexto):

    api = contexto["api"]

    paciente = contexto["datos"]["paciente"]

    response = api.post(
        "pacientes",
        paciente
    )

    assert_status(response, 422)

    data = assert_json(response)

    return (
        "Registro duplicado rechazado correctamente. "
        + data.get("message", "")
    )