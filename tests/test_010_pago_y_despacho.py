import os

from core.assertions import (
    assert_status,
    assert_json,
    assert_true
)


def ejecutar(contexto):

    api = contexto["api"]

    receta_id = contexto["datos"]["receta_id"]

    pago = {

        "receta_id": receta_id,

        "metodo_pago_id":
            int(os.getenv("QA_METODO_PAGO_ID")),

        "usuario_id":
            int(os.getenv("QA_USUARIO_ID")),

        "observaciones":
            "Pago de receta mediante automatización QA"
    }

    respuesta_pago = api.post(
        "pago-recetas",
        pago
    )

    assert_status(respuesta_pago, 201)

    pago_data = assert_json(respuesta_pago)

    assert_true(
        pago_data.get("pago") is not None,
        "No se generó el pago de la receta."
    )

    assert_true(
        pago_data.get("comprobante") is not None,
        "No se generó el comprobante."
    )

    assert_true(
        float(pago_data.get("total", 0)) > 0,
        "El total de la receta no es válido."
    )

    despacho = {

        "receta_id": receta_id,

        "usuario_id":
            int(os.getenv("QA_USUARIO_ID")),

        "observaciones":
            "Despacho generado por automatización QA"
    }

    respuesta_despacho = api.post(
        "despachos-receta",
        despacho
    )

    assert_status(respuesta_despacho, 201)

    despacho_data = assert_json(respuesta_despacho)

    assert_true(
        despacho_data.get("despacho") is not None,
        "No se generó el registro de despacho."
    )

    receta_final = api.get(
        f"recetas/{receta_id}"
    )

    assert_status(receta_final, 200)

    receta_data = assert_json(receta_final)

    assert_true(
        receta_data.get("estado") == "DESPACHADA",
        "La receta no cambió a DESPACHADA."
    )

    return (
        "Pago realizado, comprobante generado "
        "y receta despachada correctamente."
    )