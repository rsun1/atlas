from atlas.app.agents.base import Agent
from atlas.app.models import PlanStep, new_id
from atlas.app import llm 
from atlas.app import memory

class Planner(Agent):
    name = "planner"
    role = "task decomposition"
    system = "You are a planning agent. Read users task and make decompositions to process the work."

    async def plan(self,task):
        if llm.is_demo():
            return [
                PlanStep(id=new_id("step"),agent="coder",command=f"Write and run code to work towards: {task.goal}"),
                PlanStep(id=new_id("step"),agent="verifier",command="Verify the result matches the goal."),
            ]
        data = await llm.complete_json(self.system, f"Goal: {task.goal}\nReturn a JSON list of steps, each with 'agent' and 'command'.")
        return [PlanStep(id=new_id("step"),agent=item["agent"],command=item["command"]) for item in data]

    async def synthesize(self, task):
        if llm.is_demo():
            return f"[DEMO] Final report for goal '{task.goal}': all steps completed."
        context = memory.working_context(task.id,max_notes=20)
        prompt = f"Goal: {task.goal}\nWrite a final report summarizing the following work: \n{context}"
        return await llm.complete(self.system, prompt)