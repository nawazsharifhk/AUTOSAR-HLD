from fastapi import APIRouter
from backend.services.ml_analytics_service import get_full_analytics_report, SCORING_RUBRIC, get_total_score

router = APIRouter(prefix="/api/analytics", tags=["ML Analytics & Evaluation Metrics"])

@router.get("/metrics")
def get_metrics_report():
    """
    Returns full evaluation metrics breakdown according to syllabus/industrial criteria:
    Metrics 1 through 12, EDA, Feature Engineering, Model Training, Evaluation, MLOps & Responsible AI.
    """
    return get_full_analytics_report()

@router.get("/rubric")
def get_rubric():
    """Returns the itemized evaluation rubric and scoring."""
    return {
        "rubric": SCORING_RUBRIC,
        "score_summary": get_total_score()
    }
