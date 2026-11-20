import os, json, uuid
from pathlib import Path
from datetime import date, datetime

import streamlit as st
from dotenv import load_dotenv

from services.api_client import APIClient
from core.runner import ejecutar_pruebas, DEPENDENCIAS
from core.suites import SUITES
from main import crear_pruebas
from diagnostico.registry import MODULOS
from diagnostico.engine import ejecutar_diagnostico, guardar_resultados
from reporting.reports import generar_reportes
from reporting.emailer import enviar_reportes, validar_email
from performance.load_test import ejecutar_carga_get
from ai_assistant.gherkin import generar_gherkin
from utils.logger import configurar_logger

load_dotenv()
st.set_page_config(page_title="Plataforma QA | Centro de Salud Respiratorio",layout="wide")
st.title("Plataforma de Automatización QA")
st.caption("Centro de Salud Respiratorio · Diagnóstico API · Pruebas funcionales y no funcionales")

def env(k,default=""): return os.getenv(k,default)

def crear_cliente(url,user,password,timeout):
    api=APIClient(url,int(timeout)); api.login(user,password); return api

def cerrar(api):
    try: api.post("logout")
    except Exception: pass

def ampliar(ids):
    final=set(ids)
    def add(i):
        for dep in DEPENDENCIAS.get(i,[]):
            if dep not in final: final.add(dep); add(dep)
    for i in list(final): add(i)
    return final

def guardar_diag_completo(rows):
    folder=Path("reports/diagnostico"); folder.mkdir(parents=True,exist_ok=True)
    name=datetime.now().strftime("diagnostico_completo_%Y%m%d_%H%M%S_%f.json")
    path=folder/name
    path.write_text(json.dumps({"fecha":datetime.now().isoformat(),"resultados":rows},ensure_ascii=False,indent=2),encoding="utf-8")
    return path

with st.sidebar:
    st.header("Conexión API")
    api_url=st.text_input("URL base",env("API_BASE_URL","http://127.0.0.1:8000/api"))
    username=st.text_input("Usuario",env("API_USERNAME","admin"))
    password=st.text_input("Contraseña",env("API_PASSWORD"),type="password")
    timeout=st.number_input("Timeout API (segundos)",min_value=5,max_value=180,value=int(env("REQUEST_TIMEOUT","30")))
    st.divider()
    

tabs=st.tabs(["Panel general","Diagnóstico por módulos","Suites funcionales","Pruebas no funcionales","Lógica del negocio","Asistente IA","Reportes","Configuración"])

with tabs[0]:
    st.subheader("Centro de control")
    cases=crear_pruebas()
    endpoints=sum(len(m["endpoints"]) for m in MODULOS.values())
    a,b,c,d=st.columns(4)
    a.metric("Módulos",len(MODULOS)); b.metric("Endpoints GET",endpoints); c.metric("Casos funcionales",len(cases)); d.metric("Suites",len(SUITES)-1)
    st.markdown("""
    **Dos líneas de ejecución**
    - Diagnóstico por módulos: consultas GET de solo lectura.
    - Pruebas funcionales: los diez casos de lógica del negocio.
    - Pruebas no funcionales: carga ligera sobre GET.
    - Asistente IA: propuesta de escenarios Gherkin para revisión humana.
    """)
    st.info("Los resultados se basan en respuestas reales. No se fuerzan estados PASS ni se eliminan registros.")

with tabs[1]:
    st.subheader("Diagnóstico técnico por módulos")
    st.write("Evalúa endpoints GET sin insertar, actualizar ni eliminar registros.")
    mode=st.radio("Tipo de diagnóstico",["Seleccionar un módulo","Ejecutar todos los módulos"],horizontal=True,key="diag_mode")
    limit=st.number_input("Tiempo máximo esperado por endpoint (ms)",100,60000,1500,100,key="diag_limit")
    show_real=st.checkbox("Mostrar datos reales de la API",value=False,key="diag_real")
    if show_real: st.warning("Modo completo: respuestas y JSON pueden contener datos personales o clínicos. No compartas estos archivos.")
    else: st.info("Modo protegido: se redactan campos personales y clínicos en las respuestas almacenadas.")
    if mode=="Seleccionar un módulo":
        module=st.selectbox("Módulo",list(MODULOS.keys()))
        definition=MODULOS[module]
        st.write(definition["descripcion"])
        st.dataframe([{"Endpoint":e["nombre"],"Método":"GET","Ruta":"/"+e["path"],"HTTP esperado":e.get("expected",[200]),"En route:list": "Sí" if e.get("verificado_en_proyecto") else "Pendiente"} for e in definition["endpoints"]],use_container_width=True,hide_index=True)
        run=st.button("Ejecutar diagnóstico del módulo",type="primary",use_container_width=True,key="diag_one")
        if run:
            if not api_url or not username or not password: st.error("Configura la conexión API.")
            else:
                api=None
                try:
                    with st.spinner(f"Evaluando {module}..."):
                        api=crear_cliente(api_url,username,password,timeout)
                        rows=ejecutar_diagnostico(api,module,definition,limit,mostrar_datos_reales=show_real)
                        path=guardar_resultados(rows,module)
                    st.session_state["diag_rows"]=rows; st.session_state["diag_path"]=str(path)
                    st.success("Diagnóstico terminado.")
                except Exception as exc: st.error(f"{type(exc).__name__}: {exc}")
                finally:
                    if api: cerrar(api)
    else:
        st.warning("Se ejecutará una consulta por cada endpoint configurado.")
        if st.button("Ejecutar diagnóstico completo",type="primary",use_container_width=True,key="diag_all"):
            api=None; rows=[]; progress=st.progress(0); status=st.empty()
            try:
                api=crear_cliente(api_url,username,password,timeout)
                for i,(name,definition) in enumerate(MODULOS.items(),1):
                    status.write(f"Evaluando {name} ({i}/{len(MODULOS)})")
                    rows.extend(ejecutar_diagnostico(api,name,definition,limit,mostrar_datos_reales=show_real))
                    progress.progress(i/len(MODULOS))
                path=guardar_diag_completo(rows)
                st.session_state["diag_rows"]=rows; st.session_state["diag_path"]=str(path)
                st.success("Diagnóstico completo finalizado.")
            except Exception as exc: st.error(f"{type(exc).__name__}: {exc}")
            finally:
                if api: cerrar(api)
    if "diag_rows" in st.session_state:
        rows=st.session_state["diag_rows"]
        passed=sum(x["estado"]=="PASS" for x in rows); failed=sum(x["estado"]=="FAIL" for x in rows)
        x,y,z=st.columns(3); x.metric("Endpoints",len(rows)); y.metric("PASS",passed); z.metric("FAIL",failed)
        st.dataframe([{"Módulo":r["modulo"],"Endpoint":r["nombre"],"Ruta":r["path"],"HTTP":r.get("http","—"),"ms":r.get("duracion_ms"),"Registros":r.get("registros","—"),"Estado":r["estado"],"Error":r.get("error_tipo",""),"Diagnóstico":r["diagnostico"]} for r in rows],use_container_width=True,hide_index=True)
        for r in rows:
            with st.expander(f"{r['estado']} · {r['modulo']} · GET /{r['path']}"):
                st.write(r["diagnostico"]); st.write("Validaciones:",r.get("validaciones",[]))
                st.write("Campos:",r.get("campos_primer_registro",[]))
                st.code(r.get("respuesta","Sin respuesta"),language="json")
        p=Path(st.session_state["diag_path"])
        if p.exists(): st.download_button("Descargar evidencia JSON",p.read_bytes(),file_name=p.name,mime="application/json")

with tabs[2]:
    st.subheader("Suites funcionales")
    suite_names=[n for n,v in SUITES.items() if v["tipo"]=="FUNCIONAL"]
    suite=st.selectbox("Suite",suite_names,key="functional_suite")
    st.write(SUITES[suite]["descripcion"])
    all_cases=crear_pruebas(); by_id={p.id:p for p in all_cases}
    defaults=SUITES[suite]["casos"]
    selected=st.multiselect("Casos de la suite (puedes ajustar)",list(by_id),default=defaults,format_func=lambda x:f"{x} — {by_id[x].nombre}",key="suite_cases")
    st.caption("Las dependencias necesarias se agregan automáticamente. Una dependencia fallida puede dejar casos posteriores en SKIPPED.")
    st.divider()
    recipient=st.text_input("Correo destinatario de reportes",value=env("QA_REPORT_EMAIL",""),key="suite_email")
    send_mail=st.checkbox("Enviar automáticamente PDF y HTML al finalizar",value=True,key="suite_send")
    confirm=st.checkbox("Confirmo que la API apunta a un ambiente de pruebas y autorizo operaciones de escritura.",key="suite_confirm")
    if st.button("Ejecutar suite funcional",type="primary",use_container_width=True):
        if not selected: st.error("Selecciona al menos un caso.")
        elif not confirm: st.error("Confirma que utilizas un ambiente de pruebas.")
        elif send_mail and not validar_email(recipient): st.error("Ingresa un correo destinatario válido.")
        elif not api_url or not username or not password: st.error("Configura la conexión API.")
        else:
            api=None; start=datetime.now(); run_id=uuid.uuid4().hex[:12]
            try:
                os.environ.update({"API_BASE_URL":api_url,"API_USERNAME":username,"API_PASSWORD":password,"REQUEST_TIMEOUT":str(int(timeout))})
                api=crear_cliente(api_url,username,password,timeout)
                cfg={
                    "paciente":{"ci":None,"nombres":"Paciente QA","apellido_paterno":"Automatizacion","apellido_materno":"Prueba","fecha_nacimiento":"1995-06-15","sexo_id":1}
                }
                context={"api":api,"datos":{},"config":cfg}
                chosen=ampliar(selected)
                if chosen-set(selected): st.info("Prerrequisitos agregados: "+", ".join(sorted(chosen-set(selected))))
                progress=st.progress(0); table=st.empty()
                def update(test,acc):
                    progress.progress(len(acc)/len(chosen))
                    table.dataframe([{"ID":p.id,"Caso":p.nombre,"Estado":p.estado,"Duración":p.duracion,"Error":p.error_tipo,"Resultado":p.resultado} for p in acc],use_container_width=True,hide_index=True)
                results=ejecutar_pruebas(all_cases,context,seleccionadas=chosen,al_actualizar=update)
                end=datetime.now()
                metadata={"run_id":run_id,"ambiente":env("QA_ENVIRONMENT","QA local"),"tipo":"FUNCIONAL","suite":suite,
                    "inicio":start.isoformat(timespec="seconds"),"fin":end.isoformat(timespec="seconds"),
                    "destinatario":recipient if send_mail else "No solicitado"}
                pdf,html_path,summary=generar_reportes(results,metadata)
                st.session_state["last_run"]={"results":results,"pdf":pdf,"html":html_path,"summary":summary}
                counts=summary["conteos"]
                a, b, c, d = st.columns(4)

                a.metric("Total", summary["total"])
                b.metric("PASS", counts["PASS"])
                c.metric("FAIL", counts["FAIL"])
                d.metric("SKIPPED", counts["SKIPPED"])
                if send_mail:
                    try:
                        enviar_reportes(recipient,pdf,html_path,f"Reporte QA - {suite} - {run_id}")
                        st.success(f"Reportes PDF y HTML enviados a {recipient}.")
                    except Exception as mail_exc:
                        st.error(f"Las pruebas y reportes se generaron, pero el correo no se pudo enviar: {type(mail_exc).__name__}: {mail_exc}")
                if counts["FAIL"]: st.error("La ejecución contiene fallos reales.")
                elif counts["SKIPPED"]: 
                    st.warning("Hay casos omitidos por dependencias.")
                else: st.success("Todos los casos ejecutados finalizaron PASS.")
            except Exception as exc: st.exception(exc)
            finally:
                if api: cerrar(api)
    if "last_run" in st.session_state:
        last=st.session_state["last_run"]
        st.subheader("Última ejecución")
        st.dataframe([{"ID":p.id,"Caso":p.nombre,"Estado":p.estado,"Duración (s)":p.duracion,"Tipo de error":p.error_tipo,"Resultado":p.resultado} for p in last["results"]],use_container_width=True,hide_index=True)
        c1,c2=st.columns(2)
        c1.download_button("Descargar informe detallado PDF",Path(last["pdf"]).read_bytes(),Path(last["pdf"]).name,"application/pdf")
        c2.download_button("Descargar reporte HTML",Path(last["html"]).read_bytes(),Path(last["html"]).name,"text/html")

with tabs[3]:
    st.subheader("Pruebas no funcionales · Performance GET")
    st.warning("Esta prueba genera solicitudes concurrentes de solo lectura. Empieza con valores pequeños y ejecútala únicamente contra un entorno autorizado de QA.")
    module=st.selectbox("Módulo a someter a carga",list(MODULOS.keys()),key="perf_module")
    available=MODULOS[module]["endpoints"]
    chosen_paths=st.multiselect("Endpoints GET", [e["path"] for e in available],default=[available[0]["path"]],key="perf_paths")
    requests_count=st.number_input("Número total de solicitudes",min_value=1,max_value=500,value=20)
    workers=st.number_input("Concurrencia",min_value=1,max_value=20,value=5)
    perf_email=st.text_input("Correo para reportes de rendimiento (opcional)",value=env("QA_REPORT_EMAIL",""),key="perf_email")
    if st.button("Ejecutar prueba de rendimiento GET",type="primary"):
        if not chosen_paths: st.error("Selecciona al menos un endpoint.")
        elif perf_email and not validar_email(perf_email): st.error("El correo de rendimiento no tiene formato válido.")
        elif not username or not password: st.error("Configura credenciales.")
        else:
            api=None
            try:
                api=crear_cliente(api_url,username,password,timeout)
                result=ejecutar_carga_get(api_url,api.token,chosen_paths,int(requests_count),int(workers),int(timeout))
                st.session_state["last_perf"]=result
                from core.test_case import TestCase
                perf_case=TestCase(
                    id="PERF-001", nombre=f"Carga GET - {module}", categoria="PERFORMANCE",
                    ejecutar=lambda ctx: "Ejecución de carga GET", tipo="NO FUNCIONAL", suite="Performance GET",
                    objetivo="Medir latencia y tasa de respuestas HTTP 2xx bajo concurrencia controlada.",
                    precondiciones="API accesible y token autorizado; endpoints GET seleccionados.",
                    pasos=[f"Enviar {result['total']} solicitudes GET con concurrencia {int(workers)}",
                           f"Calcular promedio {result['promedio_ms']} ms y P95 {result['p95_ms']} ms"],
                    esperado="Las solicitudes deben responder sin errores de infraestructura.",
                    obtenido=f"Exitosas: {result['exitos']}; fallidas: {result['fallidos']}; promedio: {result['promedio_ms']} ms; P95: {result['p95_ms']} ms",
                    resultado=json.dumps(result,ensure_ascii=False)[:3000],
                    estado="PASS" if result["fallidos"]==0 else "FAIL",
                    duracion=round(sum(x["duracion_ms"] for x in result["resultados"])/1000,3)
                )
                rid=uuid.uuid4().hex[:12]; now=datetime.now().isoformat(timespec="seconds")
                perf_pdf,perf_html,_=generar_reportes([perf_case],{
                    "run_id":rid,"ambiente":env("QA_ENVIRONMENT","QA local"),"tipo":"NO FUNCIONAL",
                    "suite":"Performance GET","inicio":now,"fin":datetime.now().isoformat(timespec="seconds"),
                    "destinatario":perf_email if perf_email else "No indicado"
                })
                st.session_state["last_perf_reports"]=(perf_pdf,perf_html)
                if perf_email and validar_email(perf_email):
                    try:
                        enviar_reportes(perf_email,perf_pdf,perf_html,f"Reporte QA Performance GET - {rid}")
                        st.success(f"Reportes de rendimiento enviados a {perf_email}.")
                    except Exception as mail_exc:
                        st.warning(f"Prueba terminada; no se pudo enviar el correo: {mail_exc}")
                st.success("Prueba GET finalizada y reportes generados.")
            except Exception as exc: st.error(f"{type(exc).__name__}: {exc}")
            finally:
                if api: cerrar(api)
    if "last_perf" in st.session_state:
        r=st.session_state["last_perf"]
        a,b,c,d,e=st.columns(5)
        a.metric("Solicitudes",r["total"]); b.metric("HTTP 2xx",r["exitos"]); c.metric("Fallidas",r["fallidos"]); d.metric("Promedio",f"{r['promedio_ms']} ms"); e.metric("P95",f"{r['p95_ms']} ms")
        st.dataframe(r["resultados"],use_container_width=True,hide_index=True)
        if "last_perf_reports" in st.session_state:
            ph,hh=st.session_state["last_perf_reports"]
            c1,c2=st.columns(2)
            c1.download_button("Descargar informe PDF",Path(ph).read_bytes(),Path(ph).name,"application/pdf")
            c2.download_button("Descargar reporte HTML",Path(hh).read_bytes(),Path(hh).name,"text/html")

with tabs[4]:
    st.subheader("Lógica del negocio · ejecución personalizada")
    st.warning("Estos casos realizan operaciones reales y pueden crear pacientes, citas, pagos, consultas y recetas. Utiliza una base de datos de pruebas.")
    cases=crear_pruebas(); names={p.id:p.nombre for p in cases}
    chosen=st.multiselect("Seleccionar casos",list(names),default=list(names),format_func=lambda x:f"{x} — {names[x]}",key="manual_cases")
    recipient2=st.text_input("Correo destinatario",value=env("QA_REPORT_EMAIL",""),key="manual_email")
    send2=st.checkbox("Enviar automáticamente PDF y HTML",value=True,key="manual_send")
    confirmed=st.checkbox("Confirmo uso de base de datos de pruebas",key="manual_confirm")
    if st.button("Ejecutar casos seleccionados",type="primary"):
        if not chosen: st.error("Selecciona casos.")
        elif not confirmed: st.error("Confirma ambiente de pruebas.")
        elif send2 and not validar_email(recipient2): st.error("Correo inválido.")
        else:
            api=None; start=datetime.now(); rid=uuid.uuid4().hex[:12]
            try:
                api=crear_cliente(api_url,username,password,timeout)
                context={"api":api,"datos":{},"config":{}}
                selected_ids=ampliar(chosen)
                results=ejecutar_pruebas(cases,context,seleccionadas=selected_ids)
                end=datetime.now()
                pdf,hp,meta=generar_reportes(results,{"run_id":rid,"ambiente":env("QA_ENVIRONMENT","QA local"),"tipo":"FUNCIONAL","suite":"Personalizada","inicio":start.isoformat(),"fin":end.isoformat(),"destinatario":recipient2 if send2 else "No solicitado"})
                st.session_state["last_run"]={"results":results,"pdf":pdf,"html":hp,"summary":meta}
                if send2:
                    try: enviar_reportes(recipient2,pdf,hp,f"Reporte QA - Personalizada - {rid}"); st.success("Reportes enviados.")
                    except Exception as mail_exc: st.error(f"No se pudo enviar el correo: {mail_exc}")
                st.success("Ejecución y reportes finalizados.")
            except Exception as exc: st.exception(exc)
            finally:
                if api: cerrar(api)

with tabs[5]:
    st.subheader("Asistente IA para diseño de pruebas")
    st.write("Genera una propuesta Gherkin a partir de un requerimiento. La propuesta requiere revisión humana antes de incorporarse o ejecutarse.")
    host=st.text_input("URL local de Ollama",env("OLLAMA_HOST","http://127.0.0.1:11434"))
    model=st.text_input("Modelo Ollama",env("OLLAMA_MODEL","qwen3:14b"))
    request_text=st.text_area("Requerimiento o caso de prueba",height=180,placeholder="Ejemplo: Verificar que un usuario válido pueda iniciar sesión...")
    if st.button("Generar propuesta Gherkin",type="primary"):
        try:
            with st.spinner("Consultando el modelo local..."):
                suggestion=generar_gherkin(request_text,model,host)
            st.session_state["gherkin_proposal"]=suggestion
        except Exception as exc: st.error(f"No se pudo consultar Ollama: {type(exc).__name__}: {exc}")
    if "gherkin_proposal" in st.session_state:
        st.subheader("Propuesta generada · requiere aprobación")
        st.code(st.session_state["gherkin_proposal"],language="gherkin")
        st.download_button("Descargar propuesta Gherkin",st.session_state["gherkin_proposal"],"propuesta.feature","text/plain")
        approved=st.checkbox("He revisado la propuesta y apruebo guardarla como borrador de prueba.",key="gherkin_approved")
        if st.button("Guardar propuesta revisada"):
            if not approved:
                st.error("Marca la aprobación después de revisar el contenido.")
            else:
                folder=Path("tests/generated"); folder.mkdir(parents=True,exist_ok=True)
                target=folder/f"propuesta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.feature"
                target.write_text(st.session_state["gherkin_proposal"],encoding="utf-8")
                st.success(f"Propuesta guardada en {target}. Debe implementarse y validarse antes de ejecutarla.")

with tabs[6]:
    st.subheader("Reportes y evidencias")
    for folder in ["reports/diagnostico","reports/html","reports/pdf","evidencias"]:
        path=Path(folder); files=sorted(path.glob("*"),key=lambda p:p.stat().st_mtime,reverse=True) if path.exists() else []
        with st.expander(f"{folder} ({len(files)} archivos)"):
            if not files: st.caption("Sin archivos generados.")
            for f in files[:50]:
                if f.is_file():
                    col1,col2=st.columns([4,1]); col1.write(f"{f.name} · {f.stat().st_size} bytes")
                    col2.download_button("Descargar",f.read_bytes(),f.name,key=f"dl_{folder}_{f.name}")

with tabs[7]:
    st.subheader("Configuración")
    st.write("La conexión API se configura desde la barra lateral. SMTP y Ollama se configuran mediante variables de entorno.")
    st.code("streamlit run dashboard.py",language="powershell")
    st.markdown("""
    **SMTP requerido para el envío automático**
    - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM, SMTP_USE_TLS
    - QA_REPORT_EMAIL puede definir un destinatario predeterminado.

    **IA local**
    - OLLAMA_HOST y OLLAMA_MODEL.
    - Ollama debe estar iniciado y el modelo descargado.

    **Seguridad**
    - No subir .env, tokens, contraseñas ni reportes con datos personales.
    - El diagnóstico GET no escribe en el backend.
    - Performance GET realiza solicitudes concurrentes; ajustar carga con prudencia.
    """)
