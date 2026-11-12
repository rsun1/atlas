import asyncio
from atlas.app import audit
from atlas.app.models import Event, new_id
from atlas.app.config import MAX_STEP_RETRIES
from atlas.app.agents import COMMITTEE
from atlas.app.models import StepStatus, TaskStatus, Task
from atlas.app import memory

class Orchestrator:
    def __init__(self):
        self.tasks:dict[str,"Task"] = {}
        self._subscribers: dict[str, list[asyncio.Queue]] = {}
        self._approvals: dict[str, asyncio.Future] = {}
    
    def _emit(self, task,type_, agent, message, data=None):
        event = Event(
            id = new_id("evt"),
            task_id=task.id,
            type=type_,
            agent=agent,
            message=message,
            data=data or {},
        )
        audit.record(event)
        for q in self._subscribers.get(task.id,[]):
            q.put_nowait(event.model_dump())
    
    def _set_status(self,task, status):
        task.status = status 
        self._emit(task, "status_changed",None,f"Task status changed to {status}")
        
    def get(self, task_id):
        return self.tasks.get(task_id)

    def subscribe(self, task_id):
        q = asyncio.Queue()
        self._subscribers.setdefault(task_id,[]).append(q)
        return q 
    
    def unsubscribe(self, task_id, q):
        if task_id in self._subscribers and q in self._subscribers[task_id]:
            self._subscribers[task_id].remove(q)
        
    def resolve_approval(self, task_id, approved):
        future = self._approvals.get(task_id)
        if future is None:
            return False 
        future.set_result(approved)
        return True 
    
    async def _wait_for_approval(self,task):
        future = asyncio.Future()
        self._approvals[task.id] = future 
        try:
            result = await asyncio.wait_for(future, timeout=600)
        except asyncio.TimeoutError:
            result = False 
        del self._approvals[task.id]
        return result
        
    async def _run_step(self, task, step):
        step.status = StepStatus.RUNNING
        self._emit(task, "step_started", step.agent, f"Step started: {step.command}")
        for attempt in range(MAX_STEP_RETRIES):
            try:
                agent = COMMITTEE[step.agent]
                result = await agent.run(task, step)
                step.status = StepStatus.COMPLETED
                step.result = result 
                self._emit(task, "step_completed", step.agent, f"Step completed: {step.command}")
                return 
            except Exception as e:
                step.retry += 1
                self._emit(task, "step_retry", step.agent, f"Step failed (attempt {attempt+1}): {e}")
                if attempt < MAX_STEP_RETRIES -1:
                    await asyncio.sleep(2**attempt)
        
        step.status = StepStatus.FAILED
        self._emit(task, "step_failed", step.agent, f"Step failed after {MAX_STEP_RETRIES} attemps")
        
    async def _run(self, task, auto_approve):
        self.tasks[task.id] = task 
        self._set_status(task, TaskStatus.PLANNING)
        
        planner = COMMITTEE["planner"]
        task.steps = await planner.plan(task)
        
        safety = COMMITTEE["safety"]
        task.risk = await safety.assess(task, task.steps)
        
        if task.risk.requires_approval and not auto_approve:
            self._set_status(task, TaskStatus.AWAITING_APPROVAL)
            approved = await self._wait_for_approval(task)
            if not approved:
                self._set_status(task,TaskStatus.FAILED)
                self._emit(task, "task_denied",None,"Task denied or approval timed out")
                memory.episodic_store(task.goal, "denied","Human reviewer denied the plan at the safety gate.")
                return 
        self._set_status(task, TaskStatus.RUNNING)
        while True:
            for step in task.steps:
                await self._run_step(task, step)
        
            if task.verified or task.rework_count >=1:
                break 
            
            task.rework_count +=1
            self._emit(task,"rework_triggered", None, "Verifier rejected output, triggering rework")
            for step in task.steps:
                step.status = StepStatus.PENDING
            
        task.report = await planner.synthesize(task)
        self._set_status(task, TaskStatus.COMPLETED)
        memory.episodic_store(task.goal, "completed", task.report[:100])
    
    def create_task(self, goal, auto_approve):
        task = Task(id=new_id("task"), goal=goal, auto_approve=auto_approve)
        self.tasks[task.id] = task 
        asyncio.create_task(self._run(task,auto_approve))
        return task
    
ORCHESTRATOR = Orchestrator()