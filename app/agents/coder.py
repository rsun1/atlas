from atlas.app.agents.base import Agent 
from atlas.app import llm, memory

class Coder(Agent):
    name = "coder"
    role = "code generation and execution"
    system = "You are a coder agent. You generate python code and invoke sandbox execution."
    
    async def run(self, task, step):
        if llm.is_demo():
            result = f"[DEMO] stdout: simulated run of '{step.command}'\nok=True"
        else:
            from atlas.app.tools.code_exec import run_python
            code = await llm.complete(self.system, f"Write Python code to: {step.command}")
            exec_result = await run_python(code)
            result = f"stdout: {exec_result['stdout']}\nstderr: {exec_result['stderr']}"
            
        memory.working_write(task.id, self.name,result)
        return result