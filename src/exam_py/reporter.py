# -*- coding: utf-8 -*-
import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# Importación respetando estrictamente la arquitectura modular
from database import GestorMongoDB
from rules import generar_tabla_verdad

class GeneradorReportesPDF:
    """Genera un reporte ejecutivo completo en PDF integrando estadísticas de MongoDB, gráficos y tablas de verdad."""
    def __init__(self, nombre_archivo: str = "reporte_logistico_ejecutivo.pdf"):
        self.nombre_archivo = nombre_archivo
        self.db = GestorMongoDB()

    def _generar_grafico_estadisticas(self) -> str:
        """Genera un gráfico estadístico basado en los registros reales de MongoDB o el motor lógico."""
        registros = self.db.consultar_registros("bitacora_accesos", {})
        
        if registros:
            # Contar decisiones reales de la bitácora de MongoDB
            estandar_cnt = sum(1 for r in registros if r.get("evaluacion", {}).get("acceso_estandar"))
            especial_cnt = sum(1 for r in registros if r.get("evaluacion", {}).get("inspeccion_especial"))
            denegados_cnt = len(registros) - estandar_cnt - especial_cnt
            
            categorias = ["Acceso Estándar", "Inspección Especial", "Denegados"]
            valores = [estandar_cnt, especial_cnt, max(0, denegados_cnt)]
        else:
            # Si la BD está vacía, usamos los datos teóricos de la tabla de verdad (16 casos)
            tabla = generar_tabla_verdad()
            n_A = sum(1 for f in tabla if f["A"])
            n_E = sum(1 for f in tabla if f["E"])
            categorias = ["Acceso Estándar (A)", "Inspección Especial (E)"]
            valores = [n_A, n_E]

        plt.figure(figsize=(6, 2.8))
        plt.bar(categorias, valores, color=["#28a745", "#ffc107", "#dc3545"][:len(categorias)], width=0.45)
        plt.title("Distribución de Decisiones Operativas (Agente PEAS)", fontsize=11, fontweight="bold")
        plt.ylabel("Cantidad de Casos")
        plt.tight_layout()

        ruta_img = "temp_chart.png"
        plt.savefig(ruta_img, dpi=150)
        plt.close()
        return ruta_img

    def crear_pdf(self) -> str:
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado del Reporte
        pdf.set_font("Arial", "B", 15)
        pdf.cell(0, 10, txt="LogiSmart Suite - Reporte Ejecutivo y Auditoría PEAS", ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 6, txt=f"Fecha de emisión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(4)

        # Sección 1: Análisis Estadístico y Gráfico
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, txt="1. Análisis Estadístico del Sistema Logístico", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, txt="El siguiente gráfico resume el comportamiento operativo de las decisiones de acceso y seguridad evaluadas por el agente inteligente a partir de los registros almacenados en MongoDB.")
        pdf.ln(2)

        ruta_img = self._generar_grafico_estadisticas()
        if os.path.exists(ruta_img):
            pdf.image(ruta_img, x=30, w=150)
            os.remove(ruta_img)

        pdf.ln(4)

        # Sección 2: Auditoría del Motor Lógico (Tabla de Verdad Completa)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, txt="2. Auditoría del Motor de Reglas (Tabla de Verdad - 16 Casos)", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, txt="El motor lógico formal evalúa todas las combinaciones posibles bajo las premisas P (Autorización), Q (Exceso de peso), R (Materiales peligrosos) y S (Conductor certificado), determinando el Acceso Estándar (A) y la Inspección Especial (E):")
        pdf.ln(2)

        # Cabecera de la tabla en el PDF
        pdf.set_font("Arial", "B", 8)
        pdf.set_fill_color(31, 106, 165) # Azul corporativo
        pdf.set_text_color(255, 255, 255)
        
        # Anchos de columna ajustados para texto ASCII compatible
        col_widths = [15, 15, 15, 15, 20, 24, 24, 15, 15]
        headers = ["P", "Q", "R", "S", "NOT Q", "P AND S", "R OR Q", "A", "E"]
        
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 6, h, 1, 0, "C", fill=True)
        pdf.ln()

        # Filas de la tabla de verdad importada de rules.py
        pdf.set_font("Arial", "", 8)
        pdf.set_text_color(0, 0, 0)
        tabla = generar_tabla_verdad()
        
        v = lambda b: "V" if b else "F"
        for fila in tabla:
            datos_fila = [
                v(fila["P"]), v(fila["Q"]), v(fila["R"]), v(fila["S"]),
                v(fila["no_Q"]), v(fila["P_y_S"]), v(fila["R_o_Q"]),
                v(fila["A"]), v(fila["E"])
            ]
            for i, val in enumerate(datos_fila):
                pdf.cell(col_widths[i], 5, val, 1, 0, "C")
            pdf.ln()

        pdf.ln(5)

        # Sección 3: Conclusiones
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, txt="3. Conclusiones y Recomendaciones Operativas", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, txt="El sistema demuestra una trazabilidad formal rigurosa, acoplando de forma síncrona las reglas de lógica proposicional con los actuadores del entorno logístico. Se recomienda continuar monitoreando las unidades con alertas de materiales peligrosos (R) para mitigar riesgos críticos en andenes.")

        pdf.output(self.nombre_archivo)
        return self.nombre_archivo