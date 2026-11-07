from enum import Enum
import uuid 
from pydantic import BaseModel, Field
import time
from typing import Any

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    AWAITING_APPROVAL= "awaiting_approval"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    
class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
        
class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class PlanStep(BaseModel):
    id: str 
    agent: str 
    command: str
    status: StepStatus = StepStatus.PENDING 
    retry: int = 0
    result: str | None = None

class RiskAssessment(BaseModel):
    score: int
    factors: list[str] = Field(default_factory=list)
    level: RiskLevel
    requires_approval: bool
    
class Task(BaseModel):
    id: str 
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    auto_approve: bool 
    steps: list[PlanStep] = Field(default_factory=list)
    risk: RiskAssessment | None = None
    verified: bool = False
    verification: str | None = None
    rework_count: int = 0 
    report: str | None = None
    created_at: float = Field(default_factory=time.time)
    
class CreateTaskRequest(BaseModel):
    goal:str 
    auto_approve: bool = False

class Event(BaseModel):
    id: str
    type: str
    task_id: str
    agent: str | None = None 
    message: str
    data:dict[str,Any] = Field(default_factory=dict) 
    ts: float = Field(default_factory=time.time)
    