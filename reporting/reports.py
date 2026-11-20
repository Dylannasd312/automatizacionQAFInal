import html, json
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm

def generar_reportes(resultados, metadata, carpeta="reports"):
    base=Path(carpeta); (base/"html").mkdir(parents=True,exist_ok=True); (base/"pdf").mkdir(parents=True,exist_ok=True)
    run_id=metadata.get("run_id") or datetime.now().strftime("%Y%m%d_%H%M%S")
    casos=[]
    for p in resultados:
        casos.append({"id":p.id,"nombre":p.nombre,"tipo":getattr(p,"tipo","FUNCIONAL"),"suite":getattr(p,"suite","Regression"),
          "estado":p.estado,"objetivo":getattr(p,"objetivo",""),"precondiciones":getattr(p,"precondiciones",""),
          "datos_prueba":getattr(p,"datos_prueba","Datos QA"),"pasos":getattr(p,"pasos",[]),"esperado":getattr(p,"esperado",""),
          "obtenido":getattr(p,"obtenido","") or p.resultado,"resultado":p.resultado,"duracion":p.duracion,
          "evidencia":getattr(p,"evidencia",""),"error_tipo":getattr(p,"error_tipo","")})
    total=len(casos); counts={s:sum(c["estado"]==s for c in casos) for s in ("PASS","FAIL","SKIPPED","NOT RUN")}
    duration=round(sum(float(c["duracion"] or 0) for c in casos),3)
    meta={**metadata,"total":total,"conteos":counts,"porcentaje_exito":round(counts["PASS"]*100/total,2) if total else 0,"duracion_segundos":duration}
    rows=[]
    for c in casos:
        rows.append("<tr>"+f"<td>{html.escape(c['id'])}</td><td>{html.escape(c['nombre'])}</td><td>{html.escape(c['tipo']+' / '+c['suite'])}</td><td class='state {html.escape(c['estado'])}'>{html.escape(c['estado'])}</td><td>{html.escape(c['resultado'])}</td><td>{c['duracion']} s</td>"+"</tr>")
    doc=f"""<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Reporte QA {run_id}</title><style>
    body{{font-family:Arial;margin:32px;background:#f4f6fa;color:#202938}}main{{max-width:1200px;margin:auto;background:white;padding:28px}}h1{{color:#17365d}}
    .metrics{{display:flex;gap:10px;flex-wrap:wrap}}.metric{{padding:12px;background:#eef2f7}}table{{width:100%;border-collapse:collapse;margin-top:20px}}
    td,th{{border:1px solid #d8dee8;padding:9px;text-align:left;vertical-align:top}}th{{background:#17365d;color:white}}.PASS{{color:green;font-weight:bold}}.FAIL{{color:#b42318;font-weight:bold}}.SKIPPED,.NOT-RUN{{color:#8a5b00;font-weight:bold}}</style></head><body><main>
    <h1>Reporte de automatización QA</h1><h2>Centro de Salud Respiratorio</h2><p>ID: {html.escape(run_id)} | Ambiente: {html.escape(str(meta.get('ambiente','QA local')))}</p>
    <p>Tipo: {html.escape(str(meta.get('tipo','FUNCIONAL')))} | Suite: {html.escape(str(meta.get('suite','Personalizada')))}</p>
    <p>Inicio: {html.escape(str(meta.get('inicio','')))} | Fin: {html.escape(str(meta.get('fin','')))} | Duración: {duration}s</p>
    <div class='metrics'><div class='metric'>Total {total}</div><div class='metric'>PASS {counts['PASS']}</div><div class='metric'>FAIL {counts['FAIL']}</div><div class='metric'>SKIPPED {counts['SKIPPED']}</div><div class='metric'>NOT RUN {counts['NOT RUN']}</div><div class='metric'>Éxito {meta['porcentaje_exito']}%</div></div>
    <table><tr><th>ID</th><th>Nombre</th><th>Tipo/suite</th><th>Estado</th><th>Observación</th><th>Duración</th></tr>{''.join(rows)}</table></main></body></html>"""
    hp=base/"html"/f"reporte_{run_id}.html"; hp.write_text(doc,encoding="utf-8")
    pp=base/"pdf"/f"informe_detallado_{run_id}.pdf"
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name="SmallQA",parent=styles["BodyText"],fontSize=8,leading=10))
    pdf=SimpleDocTemplate(str(pp),pagesize=landscape(A4),rightMargin=12*mm,leftMargin=12*mm,topMargin=12*mm,bottomMargin=12*mm)
    story=[Paragraph("Informe detallado de automatización QA",styles["Title"]),Paragraph("Centro de Salud Respiratorio",styles["Heading2"]),Spacer(1,8)]
    general=[["ID ejecución",run_id,"Ambiente",str(meta.get("ambiente","QA local"))],["Tipo / suite",f"{meta.get('tipo','FUNCIONAL')} / {meta.get('suite','Personalizada')}","Destinatario",str(meta.get("destinatario","No indicado"))],["Inicio",str(meta.get("inicio","")),"Fin",str(meta.get("fin",""))],["Duración",f"{duration}s","Proyecto","Centro de Salud Respiratorio"]]
    t=Table(general,colWidths=[75,220,75,250]); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.HexColor("#E8EEF6")),("BACKGROUND",(2,0),(2,-1),colors.HexColor("#E8EEF6")),("PADDING",(0,0),(-1,-1),5),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story += [t,Spacer(1,8),Paragraph(f"Resumen: total {total}; PASS {counts['PASS']}; FAIL {counts['FAIL']}; SKIPPED {counts['SKIPPED']}; NOT RUN {counts['NOT RUN']}; éxito {meta['porcentaje_exito']}%",styles["BodyText"])]
    for c in casos:
        story += [Spacer(1,10),Paragraph(f"{c['id']} — {c['nombre']} [{c['estado']}]",styles["Heading3"])]
        fields=[("Objetivo",c["objetivo"]),("Precondiciones",c["precondiciones"]),("Datos de prueba",c["datos_prueba"]),("Resultado esperado",c["esperado"]),("Resultado obtenido",c["obtenido"]),("Clasificación de error",c["error_tipo"] or "No aplica"),("Duración",f"{c['duracion']} s")]
        fields += [(f"Paso {i}",s) for i,s in enumerate(c["pasos"],1)]
        fields += [("Evidencia",c["evidencia"] or "Consultar evidencias redactadas de la ejecución."),("Observación",c["resultado"])]
        tb=Table([[Paragraph(str(a),styles["SmallQA"]),Paragraph(str(b).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"),styles["SmallQA"])] for a,b in fields],colWidths=[100,595])
        tb.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.35,colors.lightgrey),("BACKGROUND",(0,0),(0,-1),colors.HexColor("#F0F3F7")),("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),5)])); story.append(tb)
    pdf.build(story)
    jp=base/"html"/f"datos_{run_id}.json"; jp.write_text(json.dumps({"metadata":meta,"casos":casos},ensure_ascii=False,indent=2),encoding="utf-8")
    return str(pp),str(hp),meta
