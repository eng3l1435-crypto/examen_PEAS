# -*- coding: utf-8 -*-
import os
import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime

# Importación de nuestros módulos especializados (Respetando la modularidad)
from database import GestorMongoDB
from rules import evaluar_camion
from llm_service import LLMService
from reporter import GeneradorReportesPDF
from peas import PEAS_LOGISMART

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class LogiSmartGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LogiSmart Python Suite - Centro de Control Inteligente (PEAS)")
        self.geometry("950x820")

        self.llm = LLMService()
        self.db = GestorMongoDB()
        self.historial_chat = []
        self.checkboxes_registros = {}

        # Contenedor de Pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tab_peas = self.tabview.add("Diseño PEAS")
        self.tab_chat = self.tabview.add("Agente IA (PEAS)")
        self.tab_crud = self.tabview.add("Base de Datos & Bitácora")
        self.tab_reportes = self.tabview.add("Reportes PDF")

        self.setup_tab_peas()
        self.setup_tab_chat()
        self.setup_tab_crud()
        self.setup_tab_reportes()

        # Cargar los registros iniciales de la bitácora automáticamente al abrir
        self.user_read()

    # --- PESTAÑA 1: DISEÑO PEAS ---
    def setup_tab_peas(self):
        txt_peas = ctk.CTkTextbox(self.tab_peas, font=("Consolas", 12))
        txt_peas.pack(padx=10, pady=10, fill="both", expand=True)
        
        contenido = f"=== AGENTE ===\n{PEAS_LOGISMART['agente']}\n\n"
        contenido += "=== P (MEDIDAS DE DESEMPEÑO) ===\n"
        for p in PEAS_LOGISMART["P_desempeno"]:
            contenido += f" - {p}\n"
        
        contenido += "\n=== E (ENTORNO) ===\n"
        contenido += f"Descripción: {PEAS_LOGISMART['E_entorno']['descripcion']}\n"
        for k, v in PEAS_LOGISMART['E_entorno']['propiedades'].items():
            contenido += f" - {k}: {v}\n"
            
        contenido += "\n=== A (ACTUADORES) ===\n"
        for a in PEAS_LOGISMART["A_actuadores"]:
            contenido += f" - {a}\n"
            
        contenido += "\n=== S (SENSORES) ===\n"
        for s in PEAS_LOGISMART["S_sensores"]:
            contenido += f" - {s}\n"

        txt_peas.insert(ctk.END, contenido)
        txt_peas.configure(state="disabled")

    # --- PESTAÑA 2: AGENTE IA (PEAS) CON INDICADOR "PENSANDO" ---
    def setup_tab_chat(self):
        self.chat_area = ctk.CTkTextbox(self.tab_chat, font=("Arial", 13), state="disabled", wrap="word")
        self.chat_area.pack(padx=10, pady=(10, 5), fill="both", expand=True)
        self.chat_area.tag_config("user", foreground="#1f6aa5")
        self.chat_area.tag_config("ia", foreground="#2fa572")

        # Frame inferior para entrada y estado de pensamiento
        frame_inf = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        frame_inf.pack(padx=10, pady=(0, 10), fill="x")

        self.entrada_chat = ctk.CTkEntry(frame_inf, placeholder_text="Consulta al agente PEAS sobre decisiones operativas...", font=("Arial", 13))
        self.entrada_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entrada_chat.bind("<Return>", self.enviar_mensaje_chat)

        self.btn_enviar = ctk.CTkButton(frame_inf, text="Consultar Agente", width=130, command=self.enviar_mensaje_chat)
        self.btn_enviar.pack(side="right")

        # Indicador de estado ("Pensando...")
        self.lbl_estado_ia = ctk.CTkLabel(self.tab_chat, text="", font=("Arial", 12, "bold"), text_color="#ff8c00")
        self.lbl_estado_ia.pack(anchor="w", padx=10, pady=(0, 5))

    def enviar_mensaje_chat(self, event=None):
        texto = self.entrada_chat.get().strip()
        if not texto: return
        self.entrada_chat.delete(0, ctk.END)

        self.actualizar_chat(f"Usuario: {texto}\n\n", "user")
        self.historial_chat.append({"role": "user", "content": texto})
        self.btn_enviar.configure(state="disabled")
        
        # Mostrar indicador visual con color de pensamiento
        self.lbl_estado_ia.configure(text="● Agente Pensando...", text_color="#ff8c00")

        threading.Thread(target=self.proceso_llm_hilo, daemon=True).start()

    def proceso_llm_hilo(self):
        try:
            respuesta = self.llm.conversar(self.historial_chat)
            self.historial_chat.append({"role": "assistant", "content": respuesta})
            self.after(0, lambda: self.actualizar_chat(f"Agente LogiSmart: {respuesta}\n\n", "ia"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error con Ollama", str(e)))
        finally:
            self.after(0, lambda: self.btn_enviar.configure(state="normal"))
            self.after(0, lambda: self.lbl_estado_ia.configure(text=""))

    def actualizar_chat(self, texto, tag):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(ctk.END, texto, tag)
        self.chat_area.configure(state="disabled")
        self.chat_area.yview(ctk.END)

    # --- PESTAÑA 3: CRUD CON BUSCADOR Y BITÁCORA AUTOMÁTICA ---
    def setup_tab_crud(self):
        lbl = ctk.CTkLabel(self.tab_crud, text="Control de Acceso y Bitácora Operativa (Reglas PEAS)", font=("Arial", 15, "bold"))
        lbl.pack(pady=5)

        # Barra de Búsqueda / Filtro superior
        search_frame = ctk.CTkFrame(self.tab_crud, fg_color="transparent")
        search_frame.pack(padx=10, pady=5, fill="x")

        ctk.CTkLabel(search_frame, text="🔍 Buscar:").pack(side="left", padx=(0, 5))
        self.entry_buscar = ctk.CTkEntry(search_frame, placeholder_text="Filtrar por placa, ID o empresa...", width=320)
        self.entry_buscar.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.user_read()) # Filtro en tiempo real al escribir

        ctk.CTkButton(search_frame, text="Limpiar Filtro", width=100, fg_color="gray", command=self.limpiar_filtro).pack(side="left", padx=5)

        # Formulario de entradas
        form_frame = ctk.CTkFrame(self.tab_crud)
        form_frame.pack(padx=10, pady=5, fill="x")

        ctk.CTkLabel(form_frame, text="Placa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_placa = ctk.CTkEntry(form_frame, placeholder_text="ABC-123-D", width=140)
        self.entry_placa.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="ID Camión:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_camion_id = ctk.CTkEntry(form_frame, placeholder_text="CAM-102", width=140)
        self.entry_camion_id.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Empresa:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.entry_empresa = ctk.CTkEntry(form_frame, placeholder_text="Logística S.A.", width=160)
        self.entry_empresa.grid(row=0, column=5, padx=5, pady=5)

        # Sensores / Premisas Lógicas (P, Q, R, S)
        rules_frame = ctk.CTkFrame(self.tab_crud)
        rules_frame.pack(padx=10, pady=5, fill="x")

        self.chk_p = ctk.CTkCheckBox(rules_frame, text="[P] Autorización previa")
        self.chk_p.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.chk_p.select()

        self.chk_q = ctk.CTkCheckBox(rules_frame, text="[Q] Exceso de peso (Báscula)")
        self.chk_q.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.chk_r = ctk.CTkCheckBox(rules_frame, text="[R] Materiales peligrosos")
        self.chk_r.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.chk_s = ctk.CTkCheckBox(rules_frame, text="[S] Conductor certificado")
        self.chk_s.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.chk_s.select()

        # Botones de Acción CRUD (Sin el botón manual de consultar, pues es automático)
        btn_frame = ctk.CTkFrame(self.tab_crud, fg_color="transparent")
        btn_frame.pack(padx=10, pady=8, fill="x")

        ctk.CTkButton(btn_frame, text="Registrar / Evaluar (Create)", fg_color="#28a745", hover_color="#218838", command=self.user_insert).pack(side="left", padx=5, expand=True)
        ctk.CTkButton(btn_frame, text="Actualizar Empresa (Update)", fg_color="#ffc107", text_color="black", hover_color="#e0a800", command=self.user_update).pack(side="left", padx=5, expand=True)
        ctk.CTkButton(btn_frame, text="Eliminar Seleccionados (Delete)", fg_color="#dc3545", hover_color="#c82333", command=self.user_delete_selected).pack(side="left", padx=5, expand=True)

        # Contenedor desplazable limpio para mostrar los registros filtrados
        lbl_bitacora = ctk.CTkLabel(self.tab_crud, text="Registros Clasificados en la Bitácora (Selecciona para eliminar):", font=("Arial", 12, "bold"))
        lbl_bitacora.pack(anchor="w", padx=10, pady=(5, 0))

        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_crud, height=210)
        self.scroll_frame.pack(padx=10, pady=5, fill="both", expand=True)

    def user_insert(self):
        placa = self.entry_placa.get().strip()
        camion_id = self.entry_camion_id.get().strip()
        empresa = self.entry_empresa.get().strip()

        if not placa or not camion_id:
            messagebox.showerror("Campos incompletos", "La 'Placa' y el 'ID del Camión' son obligatorios.")
            return

        P = bool(self.chk_p.get())
        Q = bool(self.chk_q.get())
        R = bool(self.chk_r.get())
        S = bool(self.chk_s.get())

        resultado_logica = evaluar_camion(P, Q, R, S)
        acceso_std = resultado_logica["acceso_estandar"]
        insp_esp = resultado_logica["inspeccion_especial"]

        actuadores = []
        if acceso_std: actuadores.append("Abrir barrera / Semáforo Verde")
        if insp_esp: actuadores.append("Derivar a Inspección Especial / Asignar Andén")
        if R: actuadores.append("Alarma sonora (Carga peligrosa)")
        if not acceso_std and not insp_esp: actuadores.append("Mantener barrera cerrada / Denegado")

        doc = {
            "placa": placa,
            "camion_id": camion_id,
            "empresa": empresa if empresa else "No especificada",
            "premisas": {"P": P, "Q": Q, "R": R, "S": S},
            "evaluacion": {"acceso_estandar": acceso_std, "inspeccion_especial": insp_esp},
            "actuadores": actuadores,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        cid = self.db.insertar_registro("bitacora_accesos", doc)
        if cid:
            messagebox.showinfo("Éxito", f"¡Registro creado correctamente en MongoDB!\nID: {cid}")
            self.user_read() # Actualización automática inmediata
        else:
            messagebox.showerror("Error", "No se pudo guardar el registro en la base de datos.")

    def user_read(self):
        for widget in list(self.scroll_frame.winfo_children()):
            widget.destroy()
        self.checkboxes_registros.clear()

        registros = self.db.consultar_registros("bitacora_accesos", {})
        filtro_texto = self.entry_buscar.get().strip().lower()

        # Filtrar registros localmente si hay texto en el buscador
        if filtro_texto:
            registros = [
                r for r in registros 
                if filtro_texto in r.get("placa", "").lower() or 
                   filtro_texto in r.get("camion_id", "").lower() or 
                   filtro_texto in r.get("empresa", "").lower()
            ]

        if not registros:
            lbl_vacio = ctk.CTkLabel(self.scroll_frame, text="No se encontraron registros en la bitácora.", text_color="gray")
            lbl_vacio.pack(padx=10, pady=10)
            return

        for r in registros:
            doc_id = str(r.get("_id"))
            
            info_texto = (
                f"[{r.get('timestamp', 'N/A')}] Camión: {r.get('camion_id')} | Placa: {r.get('placa')} | Empresa: {r.get('empresa')}\n"
                f"   Reglas -> A.Estándar: {r.get('evaluacion', {}).get('acceso_estandar')} | Insp.Especial: {r.get('evaluacion', {}).get('inspeccion_especial')}\n"
                f"   Actuadores: {', '.join(r.get('actuadores', []))}"
            )

            var_chk = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(self.scroll_frame, text=info_texto, variable=var_chk, font=("Consolas", 11))
            chk.pack(padx=5, pady=6, fill="x", anchor="w")
            
            self.checkboxes_registros[doc_id] = var_chk

    def limpiar_filtro(self):
        self.entry_buscar.delete(0, ctk.END)
        self.user_read()

    def user_update(self):
        camion_id = self.entry_camion_id.get().strip()
        nueva_empresa = self.entry_empresa.get().strip()

        if not camion_id or not nueva_empresa:
            messagebox.showwarning("Datos incompletos", "Para actualizar, ingresa el 'ID del Camión' y la nueva 'Empresa'.")
            return

        exito = self.db.actualizar_registro("bitacora_accesos", {"camion_id": camion_id}, {"empresa": nueva_empresa})
        if exito:
            messagebox.showinfo("Actualizado", f"El camión {camion_id} ha sido actualizado con éxito.")
            self.user_read()
        else:
            messagebox.showwarning("Aviso", f"No se encontró ningún registro con el ID: {camion_id} o no hubo cambios.")

    def user_delete_selected(self):
        ids_a_eliminar = [doc_id for doc_id, var in self.checkboxes_registros.items() if var.get()]

        if not ids_a_eliminar:
            messagebox.showwarning("Selección vacía", "Por favor marca al menos una casilla en la bitácora para eliminar.")
            return

        confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar {len(ids_a_eliminar)} registro(s) seleccionado(s)?")
        if confirmar:
            from bson.objectid import ObjectId
            eliminados = 0
            for doc_id in ids_a_eliminar:
                exito = self.db.eliminar_registro("bitacora_accesos", {"_id": ObjectId(doc_id)})
                if exito: eliminados += 1

            messagebox.showinfo("Eliminado", f"Se han eliminado {eliminados} registro(s) correctamente.")
            self.user_read()

    # --- PESTAÑA 4: REPORTES PDF ---
    def setup_tab_reportes(self):
        lbl = ctk.CTkLabel(self.tab_reportes, text="Generación de Reportes Automáticos", font=("Arial", 16, "bold"))
        lbl.pack(pady=20)

        btn_pdf = ctk.CTkButton(self.tab_reportes, text="📄 Generar Reporte Ejecutivo PDF", fg_color="#28a745", hover_color="#218838", command=self.generar_pdf)
        btn_pdf.pack(pady=10)

    def generar_pdf(self):
        try:
            reporter = GeneradorReportesPDF("reporte_logistico_ejecutivo.pdf")
            archivo = reporter.crear_pdf()
            messagebox.showinfo("Éxito", f"Reporte generado y guardado en:\n{os.path.abspath(archivo)}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el PDF:\n{e}")

def iniciar_interfaz():
    app = LogiSmartGUI()
    app.mainloop()

if __name__ == "__main__":
    iniciar_interfaz()