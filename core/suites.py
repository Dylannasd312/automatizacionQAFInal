SUITES = {
    "Smoke": {"tipo":"FUNCIONAL","descripcion":"Comprobaciones esenciales de los flujos principales.","casos":["TC-001","TC-003","TC-005"]},
    "Sanity": {"tipo":"FUNCIONAL","descripcion":"Validaciones focalizadas de reglas críticas.","casos":["TC-002","TC-004","TC-006","TC-007"]},
    "Regression": {"tipo":"FUNCIONAL","descripcion":"Conjunto amplio de los diez casos funcionales.","casos":[f"TC-{i:03d}" for i in range(1,11)]},
    "Integration": {"tipo":"FUNCIONAL","descripcion":"Interacción entre citas, pagos, consultas, recetas y farmacia.","casos":["TC-005","TC-008","TC-009","TC-010"]},
    "End-to-End": {"tipo":"FUNCIONAL","descripcion":"Flujo integrado desde registro hasta atención y despacho.","casos":["TC-001","TC-003","TC-005","TC-008","TC-009","TC-010"]},
    "Performance GET": {"tipo":"NO FUNCIONAL","descripcion":"Carga ligera configurable sobre endpoints GET de solo lectura.","casos":[]}
}
