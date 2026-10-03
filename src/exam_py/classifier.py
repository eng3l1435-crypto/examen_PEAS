import re
from datetime import datetime
from typing import Dict, List, Optional

CATEGORIAS: Dict[str, List[str]] = {
    "materiales_peligrosos": ["peligroso", "derrame", "fuga", "quimico", "inflamable", "toxico"],
    "sobrepeso": ["sobrepeso", "excede", "bascula", "exceso de peso"],
    "acceso_no_autorizado": ["sin autorizacion", "no autorizado", "acceso denegado"],
    "falla_hardware": ["camara", "sensor", "lector", "rfid"],
    "falla_software": ["sistema", "error", "pantalla", "caido", "lento"],
    "somnolencia_conductor": ["somnolencia", "dormido", "cansancio", "fatiga"]
}
PALABRAS_URGENTES = ["urgente", "emergencia", "accidente", "incendio", "critico"]
PRIORIDAD_BASE = {"materiales_peligrosos": "critica", "somnolencia_conductor": "alta", "sobrepeso": "media", "otro": "baja"}
ORDEN_PRIORIDAD = ["baja", "media", "alta", "critica"]

def procesar_incidente(remitente: str, asunto: str, cuerpo: str) -> dict:
    texto = (asunto + " " + cuerpo).lower()
    mejor_cat = "otro"
    coincidencias = []
    for cat, kws in CATEGORIAS.items():
        hallados = [kw for kw in kws if kw in texto]
        if hallados:
            mejor_cat = cat
            coincidencias = hallados
            break
            
    prioridad = PRIORIDAD_BASE.get(mejor_cat, "baja")
    if any(u in texto for u in PALABRAS_URGENTES):
        idx = min(ORDEN_PRIORIDAD.index(prioridad) + 1, len(ORDEN_PRIORIDAD) - 1)
        prioridad = ORDEN_PRIORIDAD[idx]

    m_placa = re.search(r"\b[A-Z0-9]{2,3}-\d{2,3}-[A-Z0-9]{1,2}\b", asunto.upper() + " " + cuerpo.upper())
    m_camion = re.search(r"\bCAM-\d+\b", asunto.upper() + " " + cuerpo.upper())

    return {
        "fecha_procesamiento": datetime.now().isoformat(timespec="seconds"),
        "remitente": remitente,
        "asunto_original": asunto,
        "cuerpo": cuerpo,
        "clasificacion": {"categoria": mejor_cat, "prioridad": prioridad, "palabras_clave": coincidencias},
        "datos_extraidos": {
            "placa": m_placa.group(0) if m_placa else None,
            "camion_id": m_camion.group(0) if m_camion else None
        },
        "estado": "nuevo"
    }