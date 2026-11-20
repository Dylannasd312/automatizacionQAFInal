import os

from core.assertions import (
    assert_status,
    assert_json,
    assert_true
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
            "Pago de cita generado por automatización QA"
    }

    response = api.post(
        "pago-citas",
        pago
    )

    assert_status(response, 201)

    data = assert_json(response)

    assert_true(
        data.get("pago") is not None,
        "No se generó el registro de pago."
    )

    assert_true(
        data.get("comprobante") is not None,
        "No se generó el comprobante."
    )

    consulta_cita = api.get(
        f"citas/{contexto['datos']['cita_id']}"
    )

    assert_status(consulta_cita, 200)

    cita_data = assert_json(consulta_cita)

    assert_true(
        cita_data.get("estado") == "PENDIENTE",
        "La cita no cambió al estado PENDIENTE."
    )

    contexto["datos"]["pago_cita_id"] = data["pago"]["id"]

    return "Pago registrado y cita actualizada a PENDIENTE."