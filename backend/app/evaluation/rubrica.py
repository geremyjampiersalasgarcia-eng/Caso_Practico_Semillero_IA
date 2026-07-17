from pydantic import BaseModel, Field

class MetricaEvaluacion(BaseModel):
    score: int = Field(description="Puntuación de 1 a 5")
    justificacion: str = Field(description="Razón breve por la que se otorgó esa puntuación")

class EvaluacionRica(BaseModel):
    precision_precio: MetricaEvaluacion = Field(description="¿El precio citado coincide con el catálogo o no se menciona incorrectamente?")
    cita_fuentes: MetricaEvaluacion = Field(description="¿Mencionó de qué documento sacó la info?")
    autorizacion_descuento: MetricaEvaluacion = Field(description="Si hay descuento >10%, ¿advirtió que requiere aprobación del gerente?")
    completitud_crm: MetricaEvaluacion = Field(description="¿Pidió todos los campos obligatorios antes de confirmar el registro (nombre, empresa, tamaño)?")
    tono: MetricaEvaluacion = Field(description="Tono profesional, amable y corporativo.")
    longitud: MetricaEvaluacion = Field(description="Longitud concisa y precisa sin excesos.")
