# Caso Práctico Semillero IA

> **⚠️ NOTA:** El dominio/tema específico del proyecto aún no ha sido asignado.

Mesa de Ayuda IA con agentes especializados e integrados. Este es un prototipo funcional diseñado para demostrar arquitectura, uso de RAG, LangGraph y agentes especializados.

---

## 🚀 Cómo empezar (Configuración Inicial)

### 1. Clonar el repositorio
```bash
git clone https://github.com/geremyjampiersalasgarcia-eng/Caso_Practico_Semillero_IA.git
cd Caso_Practico_Semillero_IA
```

### 2. Configurar Variables de Entorno (IMPORTANTE)

El proyecto utiliza variables de entorno para manejar credenciales de forma segura. NUNCA debes subir tus API keys al repositorio.

**Para el Backend:**
1. Navega a la carpeta del backend:
   ```bash
   cd backend
   ```
2. Copia el archivo de ejemplo para crear tu propio archivo `.env` local:
   ```bash
   cp .env.example .env
   ```
   *(En Windows puedes usar `copy .env.example .env`)*
3. Abre el nuevo archivo `.env` en tu editor de código y agrega tu clave de Gemini (y cualquier otra credencial que necesites en el futuro):
   ```env
   GOOGLE_API_KEY=tu_api_key_aqui
   ```

**Para el Frontend (próximamente):**
1. Navega a la carpeta del frontend:
   ```bash
   cd ../frontend
   ```
2. Crea tu archivo `.env.local`:
   ```bash
   cp .env.example .env.local
   ```

El archivo `.env` ya está excluido en el `.gitignore`, así que no hay riesgo de subirlo accidentalmente.

---

## 📁 Estructura del Proyecto

* **backend/**: API en FastAPI, lógica de RAG y agentes LangGraph.
* **frontend/**: Interfaz de usuario en Next.js.
* **docs/**: Documentación detallada sobre arquitectura y decisiones técnicas.