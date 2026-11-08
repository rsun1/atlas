import atlas.app.memory as memory
import atlas.app.llm as llm

class Agent:
    name = ""
    role = ""
    system = ""
    
    async def run(self, task, step):
        context = memory.working_context(task.id)
        prompt = f"Goal: {task.goal}\nStep: {step.command}\nContext: {context}"
        result = await llm.complete(self.system, prompt)
        memory.working_write(task.id,self.name,result)
        return result
    
    