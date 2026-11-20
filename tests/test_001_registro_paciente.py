from core.assertions import (
    assert_status,
    assert_json,
    assert_true
)

from utils.helpers import generar_paciente


def ejecutar(contexto):

    api = contexto["api"]

    paciente = generar_paciente()

    response = api.post(
        "pacientes",
        paciente
    )

    assert_status(response, 201)

    data = assert_json(response)

    assert_true(
        "data" in data,
        "No se encontró el paciente en la respuesta."
    )

    registro = data["data"]

    paciente_id = registro.get("id")

    assert_true(
        paciente_id is not None,
        "No se obtuvo el ID del paciente."
    )

    assert_true(
        registro.get("ci") == paciente["ci"],
        "El CI registrado no coincide."
    )

    assert_true(
        registro.get("codigo_paciente")
        == paciente["codigo_paciente"],
        "El código del paciente no coincide."
    )

    assert_true(
        registro.get("usuario") is not None,
        "No se generó el usuario del paciente."
    )

    assert_true(
        registro.get("historia_clinica") is not None
        or registro.get("historiaClinica") is not None,
        "No se generó la historia clínica."
    )

    contexto["datos"]["paciente"] = paciente

    contexto["datos"]["paciente_id"] = paciente_id

    contexto["datos"]["usuario_paciente_id"] = (
        registro["usuario"]["id"]
    )

    return (
        f"Paciente registrado correctamente. "
        f"ID: {paciente_id}"
    )