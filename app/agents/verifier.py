from atlas.app.agents.base import Agent 
from atlas.app import llm, memory 

class Verifier(Agent):
    name = "verifier"
    role = "output verification"
    system = "You are a verification agent. Check whether the completed work satisfies the goal."
    
    async def run(self, task, step):
        if llm.is_demo():
            passed, notes = True, "[DEMO] Output is consistent with the goal."
        else:
            context = memory.working_context(task.id, max_notes=20)
            data = await llm.complete_json(self.system, f"Goal: {task.goal}\nWork done: \n{context}\nReturn JSON with 'passed' (bool) and 'notes' (str).")
            passed = data.get("passed", False)
            notes = data.get("notes","")
        
        task.verified = passed 
        task.verification = notes 
        memory.working_write(task.id, self.name, notes)
        return notes