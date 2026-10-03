import itertools
from typing import Dict, List

def evaluar_camion(P: bool, Q: bool, R: bool, S: bool) -> Dict[str, bool]:
    """
    Evalúa las reglas de acceso estándar (A) e inspección especial (E) 
    mediante lógica proposicional.
    """
    for nombre, valor in (("P", P), ("Q", Q), ("R", R), ("S", S)):
        if not isinstance(valor, bool):
            raise TypeError(f"La premisa {nombre} debe ser bool")

    # A = P ∧ S ∧ ¬Q -> Autorizado, conductor certificado y sin exceso de peso
    acceso_estandar = P and S and (not Q)

    # E = P ∧ (R ∨ Q) -> Autorizado y (carga peligrosa O exceso de peso)
    inspeccion_especial = P and (R or Q)

    return {"acceso_estandar": acceso_estandar, "inspeccion_especial": inspeccion_especial}

def generar_tabla_verdad() -> List[Dict[str, bool]]:
    """
    Genera la tabla de verdad completa (2^4 = 16 filas) incluyendo 
    las columnas intermedias (¬Q, P∧S, R∨Q) para la trazabilidad.
    """
    filas: List[Dict[str, bool]] = []
    for P, Q, R, S in itertools.product([True, False], repeat=4):
        resultado = evaluar_camion(P, Q, R, S)
        filas.append({
            "P": P, "Q": Q, "R": R, "S": S,
            "no_Q": not Q,             # ¬Q
            "P_y_S": P and S,          # P ∧ S
            "R_o_Q": R or Q,           # R ∨ Q
            "A": resultado["acceso_estandar"],
            "E": resultado["inspeccion_especial"],
        })
    return filas

def obtener_tabla_verdad_formateada() -> str:
    """
    Retorna la tabla de verdad en formato de texto plano listo 
    para imprimirse en consola o mostrarse en la interfaz gráfica.
    """
    v = lambda b: "V" if b else "F"
    tabla = generar_tabla_verdad()

    lineas = []
    lineas.append("=" * 78)
    lineas.append("SECCIÓN 2 - TABLAS DE VERDAD (Motor Lógico)")
    lineas.append("=" * 78)
    lineas.append(f"{'P':^3}{'Q':^3}{'R':^3}{'S':^3} | {'¬Q':^4}{'P∧S':^6}{'R∨Q':^6} | {'A':^3}{'E':^3}")
    lineas.append("-" * 42)
    
    for f in tabla:
        lineas.append(
            f"{v(f['P']):^3}{v(f['Q']):^3}{v(f['R']):^3}{v(f['S']):^3} | "
            f"{v(f['no_Q']):^4}{v(f['P_y_S']):^6}{v(f['R_o_Q']):^6} | "
            f"{v(f['A']):^3}{v(f['E']):^3}"
        )
    
    # Conclusiones estadísticas breves para justificar en el reporte
    n_A = sum(f["A"] for f in tabla)
    n_E = sum(f["E"] for f in tabla)
    lineas.append(f"\nResumen: A es Verdadera en {n_A}/16 casos; E es Verdadera en {n_E}/16 casos.")
    return "\n".join(lineas)