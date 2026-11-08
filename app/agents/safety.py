from atlas.app.agents.base import Agent 
from atlas.app import risk 
from atlas.app import llm 

class Safety(Agent):
    name = "safety"
    role = "assess risk"
    system = "You are a safety agent. You run risk assessment on user tasks and output the risk score and factors."

    async def assess(self, task, steps):
        if llm.is_demo():
            agent_score, agent_factors = 0, []
        else:
            data = await llm.complete_json(self.system, f"Goal: {task.goal}\nReturn JSON with 'score' (0-100) and 'factors' (list of strings).")
            agent_score = data.get("score", 0)
            agent_factors = data.get("factors", [])
        
        return risk.merge(task.goal,steps,agent_score,agent_factors)