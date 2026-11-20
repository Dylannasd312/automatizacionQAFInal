import os

from core.assertions import (
    assert_status,
    assert_json,
    assert_true
)


def ejecutar(contexto):

    api = contexto["api"]

    consulta_id = contexto["datos"]["consulta_id"]

    signos = {

        "consulta_id": consulta_id,

        "temperatura": 36.5,

        "frecuencia_cardiaca": 75,

        "frecuencia_respiratoria": 18,

        "presion_arterial": "120/80",

        "saturacion_oxigeno": 98,

        "peso": 70,

        "talla": 1.74,

        "observaciones":
            "Datos ficticios para prueba QA"
    }

    respuesta_signos = api.post(
        "signos-vitales",
        signos
    )

    assert_status(respuesta_signos, 201)

    signos_data = assert_json(respuesta_signos)

    assert_true(
        signos_data.get("data") is not None,
        "No se registraron los signos vitales."
    )

    imc = signos_data["data"].get("imc")

    assert_true(
        imc is not None,
        "No se calculó el IMC."
    )

    medicamento_id = int(
        os.getenv("QA_MEDICAMENTO_ID")
    )

    receta = {

        "consulta_id": consulta_id,

        "observaciones":
            "Receta generada por automatización QA",

        "detalles": [

            {

                "medicamento_id": medicamento_id,

                "cantidad": int(
                    os.getenv("QA_CANTIDAD_MEDICAMENTO")
                ),

                "dosis": "Según indicación de prueba",

                "frecuencia": "Según indicación de prueba",

                "duracion": "Según indicación de prueba",

                "indicaciones": "Registro ficticio QA"
            }
        ]
    }

    respuesta_receta = api.post(
        "recetas",
        receta
    )

    assert_status(respuesta_receta, 201)

    receta_data = assert_json(respuesta_receta)

    registro = receta_data["data"]

    receta_id = registro.get("id")

    assert_true(
        receta_id is not None,
        "No se obtuvo el ID de la receta."
    )

    assert_true(
        registro.get("estado") == "EMITIDA",
        "La receta no está en estado EMITIDA."
    )

    contexto["datos"]["receta_id"] = receta_id

    return (
        f"Signos vitales registrados. IMC: {imc}. "
        f"Receta generada. ID: {receta_id}"
    )