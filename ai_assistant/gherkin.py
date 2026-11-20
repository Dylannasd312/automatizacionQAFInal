import requests
def generar_gherkin(texto_caso,modelo="qwen3:14b",host="http://127.0.0.1:11434",timeout=120):
    if not texto_caso.strip(): raise ValueError("Escribe un requerimiento o caso de prueba.")
    prompt=("Convierte el requerimiento en una propuesta Gherkin en español. Incluye Feature, Scenario, Given, When, Then y And. "
    "No inventes selectores, URLs ni datos no proporcionados. Enumera dudas al final. No afirmes que la prueba fue ejecutada.\\n\\n"+texto_caso)
    r=requests.post(host.rstrip("/")+"/api/generate",json={"model":modelo,"prompt":prompt,"stream":False},timeout=timeout)
    r.raise_for_status(); return r.json().get("response","").strip()
