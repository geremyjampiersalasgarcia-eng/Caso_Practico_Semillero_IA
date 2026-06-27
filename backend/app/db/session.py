# session.py - Motor y sesión de SQLAlchemy para PostgreSQL
# Crea el engine con pool_pre_ping y configura SessionLocal
# Expone get_db() como generador/dependencia para inyectar en los endpoints de FastAPI
