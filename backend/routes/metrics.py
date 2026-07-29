from fastapi import APIRouter
from backend.models.record import SystemMetrics
from backend.services.vector_store import vector_store

router = APIRouter(tags=["metrics"])

@router.get("/metrics", response_model=SystemMetrics)
def get_system_metrics():
    """Returns system performance metrics including latency and cache effectiveness statistics."""
    metrics_data = vector_store.get_metrics()
    return SystemMetrics(**metrics_data)
