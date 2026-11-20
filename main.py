import os
import yaml
from dotenv import load_dotenv

from services.auth_service import autenticar
from core.test_case import TestCase
from core.runner import ejecutar_pruebas

from tests.test_001_registro_paciente import ejecutar as tc001
from tests.test_002_paciente_duplicado import ejecutar as tc002
from tests.test_003_creacion_cita import ejecutar as tc003
from tests.test_004_fecha_cita_invalida import ejecutar as tc004
from tests.test_005_pago_cita import ejecutar as tc005
from tests.test_006_pago_duplicado import ejecutar as tc006
from tests.test_007_consulta_sin_pago import ejecutar as tc007
from tests.test_008_creacion_consulta import ejecutar as tc008
from tests.test_009_signos_y_receta import ejecutar as tc009
from tests.test_010_pago_y_despacho import ejecutar as tc010

from utils.logger import configurar_logger


def generar_html(resultados):

    os.makedirs("reports/html", exist_ok=True)

    total = len(resultados)

    aprobados = sum(
        p.estado == "PASS" for p in resultados
    )

    fallidos = sum(
        p.estado == "FAIL" for p in resultados
    )

    filas = ""

    for prueba in resultados:

        filas += f"""
        <tr>
            <td>{prueba.id}</td>
            <td>{prueba.nombre}</td>
            <td>{prueba.categoria}</td>
            <td class="{prueba.estado}">
                {prueba.estado}
            </td>
            <td>{prueba.resultado}</td>
            <td>{prueba.duracion}s</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="es">

    <head>
        <meta charset="UTF-8">

        <title>Reporte de Automatización QA</title>

        <style>

            body {{
                font-family: Arial;
                margin: 40px;
                background: #f4f6f9;
            }}

            h1 {{
                color: #17365d;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}

            th, td {{
                padding: 12px;
                border: 1px solid #ddd;
                text-align: left;
            }}

            th {{
                background: #17365d;
                color: white;
            }}

            .PASS {{
                color: green;
                font-weight: bold;
            }}

            .FAIL {{
                color: red;
                font-weight: bold;
            }}

        </style>

    </head>

    <body>

        <h1>Reporte de Automatización QA</h1>

        <h3>Centro de Salud Respiratorio</h3>

        <p>Total de pruebas: {total}</p>

        <p>Pruebas aprobadas: {aprobados}</p>

        <p>Pruebas fallidas: {fallidos}</p>

        <table>

            <thead>

                <tr>
                    <th>ID</th>
                    <th>Prueba</th>
                    <th>Tipo</th>
                    <th>Estado</th>
                    <th>Resultado</th>
                    <th>Duración</th>
                </tr>

            </thead>

            <tbody>

                {filas}

            </tbody>

        </table>

    </body>

    </html>
    """

    ruta = "reports/html/reporte.html"

    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(html)

    return ruta


def generar_pdf(resultados):

    from reportlab.lib import colors

    from reportlab.lib.pagesizes import A4, landscape

    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    from reportlab.lib.styles import getSampleStyleSheet

    os.makedirs("reports/pdf", exist_ok=True)

    ruta = "reports/pdf/reporte.pdf"

    documento = SimpleDocTemplate(
        ruta,
        pagesize=landscape(A4)
    )

    estilos = getSampleStyleSheet()

    contenido = []

    contenido.append(
        Paragraph(
            "Reporte de Automatización QA",
            estilos["Title"]
        )
    )

    contenido.append(
        Paragraph(
            "Centro de Salud Respiratorio",
            estilos["Heading2"]
        )
    )

    contenido.append(Spacer(1, 20))

    datos = [
        [
            "ID",
            "Prueba",
            "Estado",
            "Duración",
            "Resultado"
        ]
    ]

    for prueba in resultados:

        datos.append([
            prueba.id,
            Paragraph(prueba.nombre, estilos["Normal"]),
            prueba.estado,
            f"{prueba.duracion}s",
            Paragraph(prueba.resultado[:250], estilos["Normal"])
        ])

    tabla = Table(
        datos,
        repeatRows=1,
        colWidths=[55, 135, 65, 65, 350]
    )

    tabla.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("VALIGN", (0, 0), (-1, -1), "TOP"),

        ("PADDING", (0, 0), (-1, -1), 7),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F0F3F7")
        ])

    ]))

    contenido.append(tabla)

    documento.build(contenido)

    return ruta


def main():

    load_dotenv()

    logger = configurar_logger()

    print("\nAUTOMATIZACIÓN QA")
    print("CENTRO DE SALUD RESPIRATORIO\n")

    try:

        # Cargar configuración
        with open(
            "config/config.yaml",
            "r",
            encoding="utf-8"
        ) as archivo:

            configuracion = yaml.safe_load(archivo)

        print("Configuración cargada.")

        # Autenticación
        print("\nIniciando autenticación...")

        api = autenticar()

        print("Token Sanctum obtenido.")

        # Contexto compartido
        contexto = {

            "api": api,

            "datos": {}
        }

        # Definición de pruebas
        pruebas = [

            TestCase(
                "TC-001",
                "Registro de paciente",
                "FUNCIONAL",
                tc001
            ),

            TestCase(
                "TC-002",
                "Paciente duplicado",
                "NEGATIVA",
                tc002
            ),

            TestCase(
                "TC-003",
                "Creación de cita",
                "FUNCIONAL",
                tc003
            ),

            TestCase(
                "TC-004",
                "Fecha de cita inválida",
                "NEGATIVA",
                tc004
            ),

            TestCase(
                "TC-005",
                "Pago de cita",
                "INTEGRACIÓN",
                tc005
            ),

            TestCase(
                "TC-006",
                "Pago duplicado",
                "NEGATIVA",
                tc006
            ),

            TestCase(
                "TC-007",
                "Consulta sin pago",
                "NEGATIVA",
                tc007
            ),

            TestCase(
                "TC-008",
                "Creación de consulta",
                "INTEGRACIÓN",
                tc008
            ),

            TestCase(
                "TC-009",
                "Signos vitales y receta",
                "INTEGRACIÓN",
                tc009
            ),

            TestCase(
                "TC-010",
                "Pago y despacho de receta",
                "INTEGRACIÓN",
                tc010
            )

        ]

        # Ejecutar
        print("\nIniciando pruebas...\n")

        resultados = ejecutar_pruebas(
            pruebas,
            contexto
        )

        # Reportes
        html = generar_html(resultados)

        pdf = generar_pdf(resultados)

        # Resumen
        aprobados = sum(
            p.estado == "PASS"
            for p in resultados
        )

        fallidos = sum(
            p.estado == "FAIL"
            for p in resultados
        )

        print("\n" + "=" * 55)

        print("RESULTADOS FINALES")

        print("=" * 55)

        print(f"Total: {len(resultados)}")

        print(f"PASS: {aprobados}")

        print(f"FAIL: {fallidos}")

        print("\nReportes generados:")

        print(html)

        print(pdf)

        logger.info(
            "Ejecución terminada. PASS=%s FAIL=%s",
            aprobados,
            fallidos
        )

        # Cerrar sesión
        try:

            api.post("logout")

            print("\nSesión cerrada correctamente.")

        except Exception as error:

            logger.warning(
                "No se pudo cerrar la sesión: %s",
                error
            )

    except Exception as error:

        logger.exception(
            "Error general de automatización"
        )

        print("\nERROR:", error)


if __name__ == "__main__":

    main()


def crear_pruebas():
    from core.test_case import TestCase
    defs = [
      ("TC-001","Registro de paciente","FUNCIONAL",tc001,"Registrar paciente válido.","Usuario autenticado y catálogos maestros disponibles.",["Enviar POST /pacientes","Validar HTTP 201","Comprobar ID, usuario e historia clínica"],"Paciente creado y relacionado."),
      ("TC-002","Paciente duplicado","NEGATIVA",tc002,"Rechazar paciente duplicado.","Paciente creado por TC-001.",["Reenviar identificador duplicado","Validar rechazo"],"La API rechaza el duplicado."),
      ("TC-003","Creación de cita","FUNCIONAL",tc003,"Crear cita en horario disponible.","Paciente y horario disponibles.",["Consultar horarios y citas","Elegir espacio libre","Enviar POST /citas","Validar estado POR_PAGAR"],"Cita creada con estado POR_PAGAR."),
      ("TC-004","Fecha de cita inválida","NEGATIVA",tc004,"Rechazar fecha de cita inválida.","Usuario autenticado.",["Enviar fecha no permitida","Validar respuesta de error"],"La API rechaza la fecha."),
      ("TC-005","Pago de cita","INTEGRACIÓN",tc005,"Registrar pago de cita pendiente.","Cita creada y método de pago válido.",["Enviar pago","Validar respuesta y estado"],"Pago registrado correctamente."),
      ("TC-006","Pago duplicado","NEGATIVA",tc006,"Impedir un segundo pago de la misma cita.","Cita con pago previo.",["Repetir pago","Validar rechazo"],"La API impide el pago duplicado."),
      ("TC-007","Consulta sin pago","NEGATIVA",tc007,"Impedir consulta de cita no pagada.","Cita en estado POR_PAGAR.",["Crear cita sin pago","Intentar crear consulta","Validar rechazo"],"La API rechaza consulta sin pago."),
      ("TC-008","Creación de consulta","INTEGRACIÓN",tc008,"Crear consulta asociada a cita pagada.","Cita pagada y paciente existente.",["Enviar POST /consultas","Validar relaciones"],"Consulta creada correctamente."),
      ("TC-009","Signos vitales y receta","INTEGRACIÓN",tc009,"Registrar signos vitales y emitir receta.","Consulta válida y medicamento configurado.",["Registrar signos vitales","Emitir receta","Validar relaciones"],"Signos vitales y receta registrados."),
      ("TC-010","Pago y despacho de receta","INTEGRACIÓN",tc010,"Pagar y despachar receta.","Receta emitida y stock disponible.",["Pagar receta","Solicitar despacho","Validar estado y movimiento"],"Receta pagada y despachada.")
    ]
    integration={"TC-005","TC-008","TC-009","TC-010"}
    return [TestCase(id=x[0],nombre=x[1],categoria=x[2],ejecutar=x[3],objetivo=x[4],precondiciones=x[5],pasos=x[6],esperado=x[7],tipo="FUNCIONAL",suite="Integration" if x[0] in integration else "Regression") for x in defs]
