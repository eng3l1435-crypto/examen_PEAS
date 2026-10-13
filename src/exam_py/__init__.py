"""
==============================================================================
 LogiSmart Python Suite  -  Orquestador Principal (Arquitectura Modular)
==============================================================================
Punto de entrada oficial que coordina los módulos del sistema:
  - database.py   -> Capa de persistencia y MongoDB
  - rules.py      -> Motor de reglas lógicas y tablas de verdad
  - classifier.py -> Procesamiento y clasificación de incidentes
  - ethics.py     -> Matriz de evaluación de riesgos éticos de IA
  - peas.py       -> Definición formal del agente racional (PEAS)
  - gui.py        -> Interfaz Gráfica de Usuario (CustomTkinter)
==============================================================================
"""

import sys
import unittest
import logging

# Importaciones de los módulos especializados de la arquitectura
from database import GestorMongoDB
from rules import obtener_tabla_verdad_formateada, evaluar_camion
from classifier import procesar_incidente
from ethics import EvaluadorRiesgosIA
from peas import PEAS_LOGISMART
from gui import iniciar_interfaz

# Configuración global de logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("logismart.main")


def ejecutar_demo_consola():
    """Ejecuta una demostración completa por consola de todos los módulos."""
    print("=" * 78)
    print("DEMOSTRACIÓN POR CONSOLA - LOGISMART SUITE")
    print("=" * 78)

    # 1. Marco PEAS
    print(f"Agente: {PEAS_LOGISMART['agente']}\n")

    # 2. Tablas de Verdad del Motor Lógico
    print(obtener_tabla_verdad_formateada())

    # 3. Base de Datos
    db = GestorMongoDB()
    if db.verificar_conexion():
        doc = {"placa": "ABC-123-D", "camion_id": "CAM-102", "autorizacion": True}
        cid = db.insertar_registro("camiones", doc)
        print(f" -> [CRUD] Camión insertado con ID: {cid}")
        db.eliminar_registro("camiones", {"camion_id": "CAM-102"})
    else:
        log.warning("MongoDB no disponible.")

    # 4. Clasificador de Incidentes
    res_json = procesar_incidente("operador@planta.example", "Derrame urgente", "Fuga de químico en CAM-102")
    print(f"\n[Clasificador JSON Estricto]:\n{res_json}")

    # 5. Módulo Ético
    ev = EvaluadorRiesgosIA("LogiSmart Suite")
    ev.registrar_modulo("Cámara", "Monitoreo de somnolencia")
    ev.registrar_riesgo("Cámara", "Sesgo nocturno", "sesgo", 4, 4, "Mitigación con datos diversos")
    print(f"\n[Ética Resumen]: {ev.resumen()}")
    print("\n¡Demostración por consola finalizada con éxito!")


if __name__ == "__main__":
    if "--tests" in sys.argv:
        # Ejecuta las pruebas unitarias: python logiuncodigo.py --tests
        unittest.main(argv=[sys.argv[0], "-v"])
    elif "--demo" in sys.argv:
        # Ejecuta la demo en texto: python logiuncodigo.py --demo
        ejecutar_demo_consola()
    else:
        # Por defecto, ejecuta la Interfaz Gráfica con pestañas: python logiuncodigo.py
        print("=" * 78)
        print("LOGISMART")
        print("=" * 78)
        iniciar_interfaz()