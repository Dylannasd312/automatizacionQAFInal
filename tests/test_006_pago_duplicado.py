import os

from core.assertions import (
    assert_status,
    assert_json
)


def ejecutar(contexto):

    api = contexto["api"]

    pago = {

        "cita_id":
            contexto["datos"]["cita_id"],

        "metodo_pago_id":
            int(os.getenv("QA_METODO_PAGO_ID")),

        "usuario_id":
            int(os.getenv("QA_USUARIO_ID")),

        "monto":
            float(os.getenv("QA_MONTO_CITA")),

        "observaciones":
            "Intento de pago duplicado QA"
    }

    response = api.post(
        "pago-citas",
        pago
    )

    assert_status(response, 422)

    data = assert_json(response)

    return (
        "Pago duplicado rechazado correctamente. "
        + data.get("message", "")
    )