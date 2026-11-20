# Guía del Dashboard QA

1. Configura la URL y credenciales en el panel lateral.
2. En **Diagnóstico por módulos**, selecciona un módulo y ejecuta su diagnóstico. Esta sección usa exclusivamente GET.
3. Revisa por endpoint: estado HTTP, tipo de contenido, tamaño, cantidad de registros, campos del primer registro, latencia y validaciones.
4. Descarga el resultado JSON si necesitas adjuntarlo a un informe.
5. En **Lógica del negocio**, configura IDs maestros, selecciona casos y confirma que la base es de pruebas. Los prerrequisitos se agregan automáticamente.
6. Consulta los resultados PASS, FAIL y SKIP y descarga los informes HTML/PDF.

Los endpoints candidatos están en `diagnostico/registry.py`; contrástalos con `php artisan route:list`. El sistema no inventa resultados exitosos ni elimina registros.
