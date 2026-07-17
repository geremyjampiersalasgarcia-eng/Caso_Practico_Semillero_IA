
# security.py - Capa de seguridad de la aplicación
# Manejo de JWT (generación/validación de tokens), hashing de datos sensibles
# Rate limiting con slowapi para protección contra abuso de endpoints

import re
from app.utils.logger import logger

def validar_input(texto: str) -> bool:
    """
    Valida el texto de entrada (Capa 1: Firewall) buscando patrones sospechosos.
    Devuelve True si es válido (seguro), False si es sospechoso (rechazado).
    """
    if not texto:
        return True
        
    # 1. Validación de longitud
    if len(texto) > 2000:
        logger.warning("Input rechazado: Excede longitud máxima", length=len(texto))
        return False

    texto_lower = texto.lower()

    # 2. Patrones de "ignora instrucciones"
    patrones_ignora = [
        r"ignora[\s\w]*instrucciones",
        r"olvida[\s\w]*instrucciones",
        r"ignora[\s\w]*reglas",
        r"olvida[\s\w]*reglas",
        r"ignora[\s\w]*prompt",
        r"olvida[\s\w]*prompt",
    ]
    for patron in patrones_ignora:
        if re.search(patron, texto_lower):
            logger.warning("Input rechazado: Patrón 'ignora instrucciones' detectado", patron=patron)
            return False

    # 3. Patrones de "cambio de rol"
    patrones_rol = [
        r"eres\s+un\s+(?!asistente|agente|orquestador)",
        r"eres\s+una\s+(?!asistente|agente|orquestador)",
        r"act[uú]a\s+como",
        r"comportate\s+como",
        r"ahora\s+eres",
        r"modo\s+desarrollador",
        r"\bdan\b", # DAN
    ]
    for patron in patrones_rol:
        if re.search(patron, texto_lower):
            logger.warning("Input rechazado: Patrón 'cambio de rol' detectado", patron=patron)
            return False
            
    # 4. Patrones de extracción de prompt
    patrones_leak = [
        r"repite[\s\w]*prompt",
        r"revela[\s\w]*prompt",
        r"dime[\s\w]*reglas",
        r"cuales[\s\w]*instrucciones",
        r"imprime[\s\w]*prompt",
    ]
    for patron in patrones_leak:
        if re.search(patron, texto_lower):
            logger.warning("Input rechazado: Patrón 'extracción de prompt' detectado", patron=patron)
            return False

    return True
