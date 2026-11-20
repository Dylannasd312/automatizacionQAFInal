from dataclasses import dataclass, field
from typing import Callable, List

@dataclass
class TestCase:
    id: str
    nombre: str
    categoria: str
    ejecutar: Callable
    estado: str = "NOT RUN"
    resultado: str = ""
    duracion: float = 0.0
    objetivo: str = ""
    precondiciones: str = ""
    datos_prueba: str = "Datos QA configurados desde el Dashboard"
    pasos: List[str] = field(default_factory=list)
    esperado: str = ""
    obtenido: str = ""
    evidencia: str = ""
    tipo: str = "FUNCIONAL"
    suite: str = "Regression"
    error_tipo: str = ""
