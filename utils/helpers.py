from datetime import date, datetime, timedelta, time
import uuid

def fecha_futura(dias=7):
    return (date.today() + timedelta(days=dias)).isoformat()

def fecha_pasada(dias=2):
    return (date.today() - timedelta(days=dias)).isoformat()

def generar_paciente():
    identificador = uuid.uuid4().hex[:8].upper()
    numero_ci = str(80000000 + int(identificador, 16) % 19999999)
    return {
        "codigo_paciente": f"PAC-QA-{identificador}", "ci": numero_ci,
        "nombres": "Carlos Eduardo", "apellido_paterno": "Rojas",
        "apellido_materno": "Mendoza", "fecha_nacimiento": "1995-06-15",
        "sexo_id": 1, "grupo_sanguineo_id": None, "estado_civil_id": None,
        "telefono": "70000003", "correo": f"qa_{identificador.lower()}@example.com",
        "direccion": "Zona de pruebas QA", "contacto_emergencia": "Pedro Rojas",
        "telefono_emergencia": "70000004", "parentesco_id": None
    }

def extraer_id(respuesta, clave):
    if not isinstance(respuesta, dict): return None
    if respuesta.get(clave) is not None: return int(respuesta[clave])
    for valor in respuesta.values():
        if isinstance(valor, dict):
            encontrado=extraer_id(valor,clave)
            if encontrado is not None: return encontrado
    return None

def buscar_horario_disponible(api, medico_id, especialidad_id, consultorio_id,
                              duracion_minutos=20, dias_busqueda=180):
    rh=api.get("horarios-medicos"); rh.raise_for_status()
    rc=api.get("citas"); rc.raise_for_status()
    horarios=rh.json(); citas=rc.json()
    if isinstance(horarios,dict): horarios=horarios.get("data",[])
    if isinstance(citas,dict): citas=citas.get("data",[])
    if not isinstance(horarios,list) or not isinstance(citas,list):
        raise AssertionError("La API no devolvió colecciones válidas de horarios y citas.")
    nombres_dias={"lunes":0,"martes":1,"miercoles":2,"miércoles":2,
                  "jueves":3,"viernes":4,"sabado":5,"sábado":5,"domingo":6}
    agenda=[]
    for h in horarios:
        try:
            if not h.get("estado",True): continue
            if int(h.get("medico_id") or 0)!=int(medico_id): continue
            if int(h.get("especialidad_id") or 0)!=int(especialidad_id): continue
            if int(h.get("consultorio_id") or 0)!=int(consultorio_id): continue
            dia=h.get("dia_semana") or {}
            if isinstance(dia,dict):
                if dia.get("estado") is False: continue
                nombre=str(dia.get("nombre","")).strip().lower()
            else: nombre=str(dia).strip().lower()
            weekday=nombres_dias.get(nombre)
            if weekday is None: continue
            inicio=time.fromisoformat(str(h["hora_inicio"])[:8])
            fin=time.fromisoformat(str(h["hora_fin"])[:8])
            agenda.append((weekday,inicio,fin))
        except (ValueError,TypeError,KeyError):
            continue
    if not agenda:
        raise AssertionError("No se encontró un horario activo para el médico, especialidad y consultorio configurados.")
    ocupados=set()
    for c in citas:
        try:
            if int(c.get("medico_id") or 0)==int(medico_id):
                ocupados.add((str(c.get("fecha_cita",""))[:10],str(c.get("hora_cita",""))[:8]))
        except (ValueError,TypeError):
            continue
    ahora=datetime.now()
    for offset in range(1,dias_busqueda+1):
        dia=date.today()+timedelta(days=offset)
        for weekday,hora_inicio,hora_fin in agenda:
            if dia.weekday()!=weekday: continue
            cursor=datetime.combine(dia,hora_inicio)
            fin_dt=datetime.combine(dia,hora_fin)
            while cursor+timedelta(minutes=duracion_minutos)<=fin_dt:
                clave=(dia.isoformat(),cursor.strftime("%H:%M:%S"))
                if cursor>ahora and clave not in ocupados:
                    return {"fecha":clave[0],"hora":clave[1]}
                cursor+=timedelta(minutes=duracion_minutos)
    raise AssertionError(f"No se encontró un horario libre durante los próximos {dias_busqueda} días.")
