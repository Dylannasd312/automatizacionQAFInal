import logging, time
from datetime import datetime

DEPENDENCIAS = {
 "TC-002":["TC-001"],"TC-003":["TC-001"],"TC-004":["TC-001"],
 "TC-005":["TC-001","TC-003"],"TC-006":["TC-001","TC-003","TC-005"],
 "TC-007":["TC-001"],"TC-008":["TC-001","TC-003","TC-005"],
 "TC-009":["TC-001","TC-003","TC-005","TC-008"],
 "TC-010":["TC-001","TC-003","TC-005","TC-008","TC-009"]
}

def _tipo_error(error):
    nombre=type(error).__name__.lower(); mensaje=str(error).lower()
    marcas=("connectionerror","timeout","connection refused","max retries exceeded","failed to establish")
    return "INFRAESTRUCTURA" if any(x in nombre or x in mensaje for x in marcas) else "FUNCIONAL"

def ejecutar_pruebas(pruebas, contexto, seleccionadas=None, al_actualizar=None):
    logger=logging.getLogger("QA"); resultados=[]; estados={}
    seleccionadas=set(seleccionadas or [p.id for p in pruebas])
    inicio=datetime.now()
    for prueba in pruebas:
        if prueba.id not in seleccionadas: continue
        faltantes=[d for d in DEPENDENCIAS.get(prueba.id,[]) if estados.get(d)!="PASS"]
        t=time.perf_counter()
        evidence_dir=__import__("pathlib").Path("evidencias")
        evidence_before=set(evidence_dir.glob("*.json")) if evidence_dir.exists() else set()
        if faltantes:
            prueba.estado="SKIPPED"; prueba.error_tipo="DEPENDENCIA"
            prueba.resultado="Prerrequisitos no aprobados: "+", ".join(faltantes)
        else:
            try:
                prueba.resultado=str(prueba.ejecutar(contexto))
                prueba.estado="PASS"; prueba.error_tipo=""; prueba.obtenido=prueba.resultado
                logger.info("%s PASS - %s",prueba.id,prueba.nombre)
            except Exception as exc:
                prueba.estado="FAIL"; prueba.error_tipo=_tipo_error(exc)
                prueba.resultado=f"{type(exc).__name__}: {exc}"; prueba.obtenido=prueba.resultado
                logger.exception("%s FAIL - %s",prueba.id,prueba.nombre)
        prueba.duracion=round(time.perf_counter()-t,3)
        evidence_after=set(evidence_dir.glob("*.json")) if evidence_dir.exists() else set()
        new_evidence=sorted(str(x) for x in (evidence_after-evidence_before))
        if new_evidence:
            prueba.evidencia=", ".join(new_evidence)
        estados[prueba.id]=prueba.estado; resultados.append(prueba)
        if al_actualizar: al_actualizar(prueba,list(resultados))
    contexto["ejecucion"]={"inicio":inicio.isoformat(),"fin":datetime.now().isoformat(),"duracion_segundos":round(sum(p.duracion for p in resultados),3)}
    return resultados
