# -*- coding: utf-8 -*-
import ollama
from typing import List, Dict

class LLMService:
    """
    Gestiona la comunicación con el modelo local en Ollama, 
    enfocado estrictamente en el rol analítico del agente PEAS de LogiSmart.
    """
    def __init__(self, modelo: str = "llama3.1"):
        self.modelo = modelo
        # El rol del agente PEAS vive aquí, encapsulado en el servicio de LLM
        self.sistema_prompt = (
            "Eres el núcleo analítico del agente inteligente LogiSmart. "
            "Tu objetivo es asistir en la toma de decisiones evaluando las medidas de desempeño (P), "
            "las propiedades del entorno logístico (E) y las acciones de los actuadores (A). "
            "Responde con precisión técnica y enfoque en automatización y seguridad logística."
        )

    def conversar(self, historial: List[Dict[str, str]]) -> str:
        """Envía el historial de chat junto con el system prompt del agente PEAS a Ollama."""
        mensajes = [{"role": "system", "content": self.sistema_prompt}] + historial
        respuesta = ollama.chat(model=self.modelo, messages=mensajes)
        return respuesta["message"]["content"]