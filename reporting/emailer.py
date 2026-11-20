import os, re, smtplib
from pathlib import Path
from email.message import EmailMessage
EMAIL_RE=re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
def validar_email(email): return bool(EMAIL_RE.fullmatch((email or "").strip()))
def enviar_reportes(destinatario,pdf_path,html_path,asunto="Reporte de automatización QA"):
    if not validar_email(destinatario): raise ValueError("Correo destinatario inválido.")
    host=os.getenv("SMTP_HOST","").strip(); port=int(os.getenv("SMTP_PORT","587"))
    user=os.getenv("SMTP_USER","").strip(); password=os.getenv("SMTP_PASSWORD","")
    sender=os.getenv("SMTP_FROM",user).strip(); tls=os.getenv("SMTP_USE_TLS","true").lower() in ("1","true","yes","si")
    if not all([host,user,password,sender]): raise RuntimeError("SMTP no configurado. Completa SMTP_HOST, SMTP_USER, SMTP_PASSWORD y SMTP_FROM en .env.")
    msg=EmailMessage(); msg["Subject"]=asunto; msg["From"]=sender; msg["To"]=destinatario.strip()
    msg.set_content("Adjuntamos el informe detallado PDF y el reporte HTML de la ejecución QA.")
    for f,mt,st in [(Path(pdf_path),"application","pdf"),(Path(html_path),"text","html")]:
        if not f.is_file(): raise FileNotFoundError(f"No existe {f}")
        msg.add_attachment(f.read_bytes(),maintype=mt,subtype=st,filename=f.name)
    with smtplib.SMTP(host,port,timeout=30) as server:
        if tls: server.starttls()
        server.login(user,password); server.send_message(msg)
    return True
