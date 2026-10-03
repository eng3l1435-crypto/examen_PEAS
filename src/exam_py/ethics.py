# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class RiesgoEtico:
    descripcion: str
    categoria: str
    probabilidad: int
    impacto: int
    mitigacion: str = ""

    @property
    def puntaje(self) -> int:
        return self.probabilidad * self.impacto

    @property
    def nivel(self) -> str:
        p = self.puntaje
        if p >= 17: return "crítico"
        if p >= 10: return "alto"
        if p >= 5: return "medio"
        return "bajo"

@dataclass
class ModuloIA:
    nombre: str
    descripcion: str = ""
    riesgos: List[RiesgoEtico] = field(default_factory=list)

class EvaluadorRiesgosIA:
    CATEGORIAS_VALIDAS = {"sesgo", "privacidad", "transparencia", "seguridad", "responsabilidad", "otro"}

    def __init__(self, nombre_sistema: str) -> None:
        self.nombre_sistema = nombre_sistema
        self._modulos: Dict[str, ModuloIA] = {}

    def registrar_modulo(self, nombre: str, descripcion: str = "") -> ModuloIA:
        if not nombre.strip(): raise ValueError("Nombre vacío")
        if nombre in self._modulos: raise ValueError("Módulo ya existe")
        mod = ModuloIA(nombre=nombre.strip(), descripcion=descripcion)
        self._modulos[nombre] = mod
        return mod

    def registrar_riesgo(self, modulo: str, descripcion: str, categoria: str, p: int, i: int, mit: str = ""):
        if modulo not in self._modulos: raise KeyError("Módulo no existe")
        if categoria not in self.CATEGORIAS_VALIDAS: raise ValueError("Categoría inválida")
        riesgo = RiesgoEtico(descripcion, categoria, p, i, mit)
        self._modulos[modulo].riesgos.append(riesgo)
        return riesgo

    def resumen(self) -> dict:
        riesgos = [(m.nombre, r) for m in self._modulos.values() for r in m.riesgos]
        por_nivel = {"crítico": 0, "alto": 0, "medio": 0, "bajo": 0}
        for _, r in riesgos: por_nivel[r.nivel] += 1
        return {"sistema": self.nombre_sistema, "total_riesgos": len(riesgos), "riesgos_por_nivel": por_nivel}