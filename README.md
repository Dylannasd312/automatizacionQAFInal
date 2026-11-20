# Plataforma de Automatización QA
## Centro de Salud Respiratorio

Plataforma Python + Streamlit para ejecutar pruebas sobre la API Laravel del Centro de Salud Respiratorio.

## Funcionalidades

1. **Diagnóstico por módulos (GET):** comprueba disponibilidad, código HTTP, respuesta JSON, estructura de colecciones, cantidad de registros, campos y latencia. No inserta, actualiza ni elimina registros.
2. **Suites funcionales:** Smoke, Sanity, Regression, Integration y End-to-End. Los diez casos existentes se mantienen y las dependencias se agregan automáticamente.
3. **Lógica del negocio:** ejecución personalizada de TC-001 a TC-010.
4. **Performance GET:** carga ligera de solo lectura con cantidad de solicitudes y concurrencia configurables. No reemplaza una prueba de estrés prolongada.
5. **Reportes:** informe PDF detallado y HTML independiente, con ID de ejecución, ambiente, fechas, duración, resumen, objetivo, precondiciones, pasos, resultados y clasificación de errores.
6. **Correo:** envío de ambos reportes como adjuntos mediante SMTP.
7. **Asistente IA:** propuesta Gherkin mediante Ollama local. La salida requiere revisión y aprobación humana, se guarda como borrador `.feature` y no determina estados PASS/FAIL ni se ejecuta automáticamente.

## Requisitos

- Windows 10/11.
- Python 3.11 o superior (probado sintácticamente con Python 3.13).
- Backend Laravel iniciado y accesible.
- Usuario API autorizado.
- Base de datos de pruebas para suites funcionales.
- Ollama local y modelo descargado, solo si se utilizará el asistente IA.
- Credenciales SMTP, solo si se enviarán reportes por correo.

## Instalación

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y configura API_USERNAME, API_PASSWORD y los IDs QA. Para el correo configura SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD y SMTP_FROM.

Inicia Laravel y ejecuta:

```powershell
streamlit run dashboard.py
```

## Flujo de demostración

1. Abrir Panel general.
2. Ejecutar diagnóstico GET por módulo.
3. Seleccionar una suite funcional o casos individuales.
4. Introducir un correo válido y habilitar envío automático.
5. Confirmar que se utiliza un ambiente de pruebas.
6. Ejecutar y revisar PASS, FAIL y SKIPPED.
7. Descargar PDF y HTML o comprobar su recepción en el correo.
8. Ejecutar Performance GET con valores moderados.
9. Generar una propuesta Gherkin con IA local y revisarla.

## Suites y cobertura

- Smoke: TC-001, TC-003 y TC-005; el ejecutor incluye los prerrequisitos necesarios.
- Sanity: TC-002, TC-004, TC-006 y TC-007; el ejecutor incluye dependencias.
- Regression: TC-001 a TC-010.
- Integration: TC-005, TC-008, TC-009 y TC-010.
- End-to-End: TC-001, TC-003, TC-005, TC-008, TC-009 y TC-010.
- Performance GET: solicitudes concurrentes de solo lectura sobre endpoints seleccionados.

Las suites agrupan los casos existentes; la clasificación no significa que se hayan validado todos los escenarios posibles de esas categorías.

## Reportes y correo

Cada ejecución funcional y de rendimiento genera un PDF y un HTML con identificador único. Si está activado el envío, ambos se adjuntan al correo destinatario. Si SMTP no está configurado o falla, la ejecución y los reportes se conservan y el Dashboard informa el error de envío.

Variables SMTP:
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- SMTP_FROM
- SMTP_USE_TLS

Nunca publiques `.env`, tokens, contraseñas ni reportes con información personal. Los cuerpos de evidencias API se redactan, y el diagnóstico ofrece modo protegido por defecto.

## Asistente IA

El asistente se conecta a Ollama local:
- OLLAMA_HOST=http://127.0.0.1:11434
- OLLAMA_MODEL=qwen3:14b

Debe estar iniciado Ollama y el modelo instalado. La IA propone Gherkin, no ejecuta ni aprueba casos.

## Seguridad y límites

- No se modifica el backend Laravel ni el esquema PostgreSQL.
- No se implementan eliminaciones físicas ni limpieza automática.
- El diagnóstico y Performance GET son de solo lectura.
- Las suites funcionales pueden crear o modificar registros. Ejecutar solo en QA.
- Las rutas de `diagnostico/registry.py` deben cotejarse con el `php artisan route:list` vigente. La marca `verificado_en_proyecto` indica que la ruta se vio en el listado compartido, no que ya haya pasado una ejecución real.
- El test de carga es moderado y configurable; no es un test soak ni un estrés de larga duración.
- La clasificación de errores funcionales/infraestructura es heurística y debe revisarse con los resultados del entorno.
- Los datos de demostración deben ser ficticios y autorizados.

## Repositorio

Antes de publicar, verifica que `.env`, `.venv`, evidencias y reportes locales no estén en el commit.
