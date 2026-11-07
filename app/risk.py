from atlas.app.config import APPROVAL_THRESHOLD
from atlas.app.models import RiskAssessment, RiskLevel


_HEURISTICS = {
    "delete": 30,
    "rm -rf": 50,
    "password": 40,
    "payment": 40,
    "production": 20,
    "ssn": 50,
}

def heuristic_score(goal, steps):
    text = goal.lower()
    for step in steps:
        text += " " + step.command.lower()
    
    score = 0
    factors = []
    for keyword, weight in _HEURISTICS.items():
        if keyword in text:
            score += weight
            factors.append(f"heuristic matched:'{keyword}'")
    score = min(100, score)
    return score, factors

def merge(goal,steps,agent_score,agent_factors):
    h_score, f_factors = heuristic_score(goal,steps)
    score = max(h_score,agent_score)
    factors = list(set(f_factors+agent_factors))
    if score >= 80:
        level = RiskLevel.HIGH
    elif score >= 50:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW
    
    requires_approval = score >= APPROVAL_THRESHOLD
    
    return RiskAssessment(score=score, factors=factors,level=level,requires_approval=requires_approval)