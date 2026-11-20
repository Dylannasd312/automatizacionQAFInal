import json, time
from datetime import datetime
from pathlib import Path

def _records(payload):
    if isinstance(payload,list): return payload
    if isinstance(payload,dict):
        for key in ("data","items","results"):
            if isinstance(payload.get(key),list): return payload[key]
    return None

def _safe_payload(payload,limit=12000,ocultar_datos=True):
    sensitive=("nombre","apellido","ci","documento","telefono","correo","email","direccion","password","token",
      "diagnostico","tratamiento","observacion","motivo","enfermedad","fecha_nacimiento","contacto_emergencia")
    def clean(value,key=""):
        if ocultar_datos and any(w in key.lower() for w in sensitive): return "[DATO OMITIDO]"
        if isinstance(value,dict): return {k:clean(v,k) for k,v in list(value.items())[:80]}
        if isinstance(value,list): return [clean(v,key) for v in value[:10]]
        return value
    try: raw=json.dumps(clean(payload),ensure_ascii=False,indent=2,default=str)
    except Exception: raw="[Respuesta no serializable]"
    return raw[:limit]

def ejecutar_diagnostico(api,modulo,definicion,timeout_objetivo=1500,mostrar_datos_reales=False):
    resultados=[]
    for endpoint in definicion["endpoints"]:
        inicio=time.perf_counter()
        item={"modulo":modulo,"nombre":endpoint["nombre"],"path":endpoint["path"],"metodo":"GET",
              "esperados":endpoint.get("expected",[200]),"verificado_en_proyecto":endpoint.get("verificado_en_proyecto",False)}
        try:
            response=api.request("GET",endpoint["path"],guardar=False); dur=round((time.perf_counter()-inicio)*1000,2)
            try: payload=response.json()
            except ValueError: payload={"texto":response.text[:3000]}
            ctype=response.headers.get("Content-Type","")
            checks=[("HTTP esperado",response.status_code in item["esperados"]),
                    ("Respuesta JSON","json" in ctype.lower() or isinstance(payload,(dict,list)))]
            records=_records(payload) if isinstance(payload,(dict,list)) else None
            if records is not None:
                checks.append(("Estructura de colección",True)); item["registros"]=len(records)
                if records: item["campos_primer_registro"]=list(records[0].keys()) if isinstance(records[0],dict) else []
            elif isinstance(payload,(dict,list)): checks.append(("Estructura JSON",True)); item["registros"]=None
            else: checks.append(("Estructura JSON",False)); item["registros"]=None
            checks.append((f"Tiempo <= {timeout_objetivo} ms",dur<=timeout_objetivo))
            item.update({"http":response.status_code,"duracion_ms":dur,"content_type":ctype,"bytes":len(response.content),
              "respuesta":_safe_payload(payload,ocultar_datos=not mostrar_datos_reales),
              "modo_visualizacion":"COMPLETO" if mostrar_datos_reales else "PROTEGIDO"})
            item["validaciones"]=[{"nombre":n,"estado":"PASS" if ok else "FAIL"} for n,ok in checks]
            item["estado"]="PASS" if all(ok for _,ok in checks) else "FAIL"
            item["diagnostico"]="; ".join(n for n,ok in checks if not ok) or "Endpoint respondió y superó las validaciones configuradas."
            item["error_tipo"]=""
        except Exception as exc:
            item.update({"estado":"FAIL","error_tipo":"INFRAESTRUCTURA","duracion_ms":round((time.perf_counter()-inicio)*1000,2),
              "diagnostico":f"{type(exc).__name__}: {exc}","validaciones":[],"respuesta":"Sin respuesta HTTP"})
        resultados.append(item)
    return resultados

def guardar_resultados(resultados,modulo):
    folder=Path("reports/diagnostico"); folder.mkdir(parents=True,exist_ok=True)
    name=datetime.now().strftime("%Y%m%d_%H%M%S_%f"); path=folder/f"diagnostico_{name}.json"
    path.write_text(json.dumps({"fecha":datetime.now().isoformat(),"modulo":modulo,"resultados":resultados},ensure_ascii=False,indent=2),encoding="utf-8")
    return path
