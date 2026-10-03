# -*- coding: utf-8 -*-
import os
import logging
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

# Carga automática del archivo .env si está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("logismart.db")

class GestorMongoDB:
    """
    Gestiona la conexión con MongoDB utilizando credenciales individuales
    obtenidas mediante variables de entorno.
    """
    def __init__(self, nombre_bd: str = "logismart_db"):
        user = os.getenv("MONGO_USER", "")
        password = os.getenv("MONGO_PASSWORD", "")
        host = os.getenv("MONGO_HOST", "localhost")
        port = os.getenv("MONGO_PORT", "27017")
        
        if user and password:
            self.uri = f"mongodb://{user}:{password}@{host}:{port}/"
        else:
            self.uri = f"mongodb://{host}:{port}/"

        self.nombre_bd = os.getenv("MONGO_DB_NAME", nombre_bd)
        self.client: Optional[MongoClient] = None
        self.db = None
        self.conectar()

    def conectar(self) -> None:
        try:
            # Enmascarar contraseña en logs por seguridad
            uri_log = self.uri
            if "@" in uri_log:
                partes = uri_log.split("@")
                uri_log = partes[0].split("//")[0] + "//***:***@" + partes[1]

            log.info("Intentando conectar a MongoDB en: %s", uri_log)
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self.client.admin.command('ping')
            self.db = self.client[self.nombre_bd]
            log.info("Conexión exitosa a MongoDB (Base de datos: '%s')", self.nombre_bd)
        except (ConnectionFailure, PyMongoError) as e:
            log.error("Fallo crítico de conexión con MongoDB: %s", e)
            self.client = None
            self.db = None

    def verificar_conexion(self) -> bool:
        if self.client is None:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except PyMongoError:
            return False

    def insertar_registro(self, coleccion: str, documento: dict) -> Optional[str]:
        if not self.verificar_conexion(): return None
        try:
            res = self.db[coleccion].insert_one(documento)
            return str(res.inserted_id)
        except PyMongoError as e:
            log.error("Error al insertar en %s: %s", coleccion, e)
            return None

    def consultar_registros(self, coleccion: str, filtro: dict = None) -> List[dict]:
        if not self.verificar_conexion(): return []
        try:
            return list(self.db[coleccion].find(filtro or {}))
        except PyMongoError as e:
            log.error("Error al consultar %s: %s", coleccion, e)
            return []

    def actualizar_registro(self, coleccion: str, filtro: dict, nuevos_datos: dict) -> bool:
        if not self.verificar_conexion(): return False
        try:
            res = self.db[coleccion].update_one(filtro, {"$set": nuevos_datos})
            return res.modified_count > 0
        except PyMongoError as e:
            log.error("Error al actualizar en %s: %s", coleccion, e)
            return False

    def eliminar_registro(self, coleccion: str, filtro: dict) -> bool:
        if not self.verificar_conexion(): return False
        try:
            res = self.db[coleccion].delete_one(filtro)
            return res.deleted_count > 0
        except PyMongoError as e:
            log.error("Error al eliminar en %s: %s", coleccion, e)
            return False

    def agregacion_incidentes_por_categoria_y_semana(self) -> List[dict]:
        if not self.verificar_conexion(): return []
        pipeline = [
            {"$project": {"categoria": "$clasificacion.categoria", "fecha": {"$toDate": "$fecha_procesamiento"}}},
            {"$group": {"_id": {"categoria": "$categoria", "semana": {"$isoWeek": "$fecha"}}, "total_incidentes": {"$sum": 1}}},
            {"$sort": {"_id.semana": -1, "total_incidentes": -1}}
        ]
        try:
            return list(self.db["incidentes"].aggregate(pipeline))
        except PyMongoError as e:
            log.error("Error en agregación de MongoDB: %s", e)
            return []