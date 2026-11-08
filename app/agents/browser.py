from atlas.app.agents.base import Agent 
from atlas.app import llm, memory

class Browser(Agent):
    name = "browser"
    role = "web search and retrieval"
    system = "You are a research agent. Extract a concise search query and summarize findings."
    
    async def run(self, task, step):
        if llm.is_demo():
            result = f"[DEMO] search results for '{step.command}': 2 mock results found and summarized."
        else:
            from atlas.app.tools.web import search, fetch_page
            query = await llm.complete(self.system, f"Extract a short search query for: {step.command}")
            results = await search(query)
            page_text = ""
            if results:
                page_text = await fetch_page(results[0]["url"])
            result = f"Search results: {results}\nPage content: {page_text[:500]}"
        memory.working_write(task.id, self.name, result)
        return result