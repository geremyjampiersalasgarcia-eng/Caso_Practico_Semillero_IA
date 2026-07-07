from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from datetime import datetime
from app.models.base import Base

class Oportunidad(Base):
    __tablename__ = "oportunidades"

    id = Column(String, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    cliente = Column(String, index=True, nullable=False)
    contacto = Column(String, nullable=False)
    producto = Column(String, index=True, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_con_descuento = Column(Float, nullable=False)
    porcentaje_descuento = Column(Float, nullable=False)
    condicion_pago = Column(String, nullable=False)
    monto_total = Column(Float, nullable=False)
    estado = Column(String, default="Registrada", nullable=False)
