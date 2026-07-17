from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import datetime

from app.db.session import get_db
from app.models.audit_log import AuditLog

router = APIRouter()

@router.get("/costs")
def get_costs_metrics(days: int = 7, db: Session = Depends(get_db)):
    """
    Devuelve los costos agregados de los últimos N días, agrupados por intención.
    """
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    
    # Costo total
    total_cost = db.query(func.sum(AuditLog.cost_usd)).filter(AuditLog.created_at >= cutoff_date).scalar() or 0.0
    
    # Costo por intención (intent_category)
    cost_by_intent = db.query(
        AuditLog.intent_category,
        func.sum(AuditLog.cost_usd).label("total_cost"),
        func.count(AuditLog.id).label("total_requests")
    ).filter(
        AuditLog.created_at >= cutoff_date
    ).group_by(
        AuditLog.intent_category
    ).all()
    
    intent_metrics = [
        {
            "intent": row.intent_category or "unknown",
            "cost_usd": float(row.total_cost or 0),
            "requests": row.total_requests
        }
        for row in cost_by_intent
    ]
    
    return {
        "period_days": days,
        "total_cost_usd": float(total_cost),
        "by_intent": intent_metrics
    }
