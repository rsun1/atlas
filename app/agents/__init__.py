from .base import Agent
from .planner import Planner
from .safety import Safety
from .coder import Coder
from .browser import Browser
from .verifier import Verifier

COMMITTEE: dict[str, Agent] = {
    "planner": Planner(),
    "safety": Safety(),
    "coder": Coder(),
    "browser": Browser(),
    "verifier": Verifier(),
}