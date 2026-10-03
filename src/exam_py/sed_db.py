# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta

# Importamos respetando la arquitectura modular
from database import GestorMongoDB
from rules import evaluar_camion

def sembrar_datos_masivos(n=100):
    """Genera e inserta n registros simulados de camiones en la bitácora de MongoDB."""
    db = GestorMongoDB()
    
    if not db.verificar_conexion():
        print("[ERROR CRÍTICO] No se pudo conectar a MongoDB. Revisa tus credenciales o el servicio.")
        return

    empresas = [
        "Transportes del Norte S.A.", 
        "Logística Global Express", 
        "CargoMex de Carga", 
        "Transp. Industriales del Bajío", 
        "Fletes y Logística del Sur",
        "Autotransportes del Pacífico"
    ]
    
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    print(f"Iniciando la inserción de {n} registros simulados en la colección 'bitacora_accesos'...")
    
    exitosos = 0
    for i in range(1, n + 1):
        # Generar datos aleatorios simulando el ingreso de vehículos
        placa_num = random.randint(100, 999)
        placa_letra1 = random.choice(letras)
        placa_letra2 = random.choice(letras)
        placa = f"{placa_letra1}{placa_letra2}-{placa_num}-X"
        
        camion_id = f"CAM-{i:03d}"
        empresa = random.choice(empresas)
        
        # Premisas lógicas (P, Q, R, S) con distribuciones lógicas realistas
        P = random.choices([True, False], weights=[85, 15])[0]  # 85% con autorización previa
        Q = random.choices([True, False], weights=[25, 75])[0]  # 25% con exceso de peso en báscula
        R = random.choices([True, False], weights=[15, 85])[0]  # 15% con materiales peligrosos
        S = random.choices([True, False], weights=[90, 10])[0]  # 90% con conductor certificado
        
        # Evaluar las reglas lógicas usando estrictamente rules.py
        resultado_logica = evaluar_camion(P, Q, R, S)
        acceso_std = resultado_logica["acceso_estandar"]
        insp_esp = resultado_logica["inspeccion_especial"]

        # Actuadores PEAS activados según la evaluación
        actuadores = []
        if acceso_std: 
            actuadores.append("Abrir barrera / Semáforo Verde")
        if insp_esp: 
            actuadores.append("Derivar a Inspección Especial / Asignar Andén")
        if R: 
            actuadores.append("Alarma sonora (Carga peligrosa)")
        if not acceso_std and not insp_esp: 
            actuadores.append("Mantener barrera cerrada / Denegado")

        # Generar un timestamp aleatorio dentro de los últimos 7 días
        dias_atras = random.randint(0, 7)
        minutos_atras = random.randint(0, 1440)
        fecha_generada = datetime.now() - timedelta(days=dias_atras, minutes=minutos_atras)

        # Documento idéntico al que genera el CRUD en gui.py
        doc = {
            "placa": placa,
            "camion_id": camion_id,
            "empresa": empresa,
            "premisas": {"P": P, "Q": Q, "R": R, "S": S},
            "evaluacion": {"acceso_estandar": acceso_std, "inspeccion_especial": insp_esp},
            "actuadores": actuadores,
            "timestamp": fecha_generada.strftime("%Y-%m-%d %H:%M:%S")
        }

        cid = db.insertar_registro("bitacora_accesos", doc)
        if cid:
            exitosos += 1

    print(f"¡Proceso finalizado! Se insertaron exitosamente {exitosos}/{n} registros.")
    print("Ya puedes abrir tu interfaz gráfica (gui.py) y verás la bitácora llena y lista para filtrar o eliminar.")

if __name__ == "__main__":
    sembrar_datos_masivos(100)