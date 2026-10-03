# -*- coding: utf-8 -*-
from typing import Dict

PEAS_LOGISMART: Dict[str, object] = {
    "agente": "Agente de control inteligente de acceso y seguridad logística LogiSmart",
    "P_desempeno": [
        "Tiempo promedio de atención por camión (minutos) -> minimizar",
        "% de camiones autorizados que ingresan sin fricción -> maximizar",
        "% de camiones no autorizados / con sobrepeso detenidos -> maximizar (meta 100%)",
        "Falsos positivos de inspección especial -> minimizar",
        "Falsos negativos (carga peligrosa que no fue inspeccionada) -> minimizar (meta 0)",
        "Incidentes de seguridad y accidentes en patio -> minimizar",
        "Tiempo de clasificación y respuesta a incidentes de soporte -> minimizar",
    ],
    "E_entorno": {
        "descripcion": "Patio de maniobras, casetas de acceso, básculas y andenes del centro logístico",
        "propiedades": {
            "observobservabilidad": "Parcialmente observable (sensores con ruido, mala visión nocturna)",
            "determinismo": "Estocástico (llegadas, clima y fallas impredecibles)",
            "episodico": "Secuencial (una decisión afecta el tráfico posterior)",
            "dinamico": "Dinámico (el entorno cambia mientras el agente decide)",
            "discreto": "Mixto (estados discretos de acceso; peso y posición continuos)",
            "agentes": "Multiagente (conductores, personal, otros sistemas)",
        },
        "actores_externos": ["Conductores", "Operadores de caseta", "Personal de seguridad", "Autoridades"],
    },
    "A_actuadores": [
        "Barrera vehicular (abrir / cerrar)",
        "Semáforo y pantallas de instrucciones al conductor",
        "Alarma sonora y luminosa",
        "Sistema de asignación de andén / carril de inspección especial",
        "Notificaciones (correo, SMS, panel) a supervisores y soporte",
        "Registro en base de datos (bitácora de accesos e incidentes)",
    ],
    "S_sensores": [
        "Cámaras con lector de placas (LPR) y cámara de somnolencia del conductor",
        "Báscula de piso (peso del vehículo)",
        "Lector RFID / QR de autorización previa",
        "Escáner de documentos (certificación del conductor)",
        "Sensores de detección de materiales peligrosos / lectura de placas de riesgo",
        "Buzón de correo de soporte (entrada de texto de incidentes)",
    ],
}