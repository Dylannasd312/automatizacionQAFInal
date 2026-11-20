import time, statistics, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
def ejecutar_carga_get(base_url,token,endpoints,solicitudes=20,concurrencia=5,timeout=15):
    if not endpoints: raise ValueError("Selecciona al menos un endpoint GET.")
    if solicitudes<1 or concurrencia<1: raise ValueError("Solicitudes y concurrencia deben ser positivas.")
    headers={"Accept":"application/json","Authorization":f"Bearer {token}"}
    def one(path):
        start=time.perf_counter()
        try:
            r=requests.get(f"{base_url.rstrip('/')}/{path.lstrip('/')}",headers=headers,timeout=timeout)
            return {"ruta":path,"http":r.status_code,"duracion_ms":round((time.perf_counter()-start)*1000,2),"error":""}
        except Exception as exc:
            return {"ruta":path,"http":None,"duracion_ms":round((time.perf_counter()-start)*1000,2),"error":f"{type(exc).__name__}: {exc}"}
    with ThreadPoolExecutor(max_workers=concurrencia) as pool:
        futures=[pool.submit(one,endpoints[i%len(endpoints)]) for i in range(solicitudes)]
        results=[f.result() for f in as_completed(futures)]
    times=[r["duracion_ms"] for r in results]; ok=sum(r["http"] is not None and 200<=r["http"]<300 for r in results)
    return {"total":len(results),"exitos":ok,"fallidos":len(results)-ok,"promedio_ms":round(statistics.mean(times),2),
      "min_ms":min(times),"max_ms":max(times),"p95_ms":sorted(times)[min(len(times)-1,int(len(times)*.95))],"resultados":results}
