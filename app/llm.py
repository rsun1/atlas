from atlas.app.config import FORCE_DEMO, ANTHROPIC_API_KEY,GROQ_API_KEY,OPENAI_API_KEY
import os 
import json

_provider = None 

def detect_provider():
    global _provider 
    if _provider is not None:
        return _provider 
    
    if FORCE_DEMO:
        _provider = "demo"
    elif ANTHROPIC_API_KEY:
        _provider = "anthropic"
    elif GROQ_API_KEY:
        _provider = "groq"
    elif OPENAI_API_KEY:
        _provider = "openai"
    else:
        _provider = "demo"
    
    return _provider

def provider():
    return detect_provider()

def is_demo():
    return detect_provider() == "demo"

def model_name():
    return "demo-model" if is_demo() else "unknown"

def _demo(system, prompt):
    return f"[DEMO] Simulated Response to: {prompt[:60]}"

async def complete(system, prompt, max_tokens=1200):
    if is_demo():
        return _demo(system, prompt)
    raise NotImplementedError("Real LLM providers not implemented yet")

def _parse_json_tolerant(text):
    start = text.find("{")
    if start == -1:
        start = text.find("[")
    end = max(text.rfind("}"),text.rfind("]"))
    
    if start == -1 or end == -1:
        return {}
    
    try:
        return json.loads(text[start:end+1])
    except json.JSONDecodeError:
        return {}
    
async def complete_json(system, prompt,max_token=1200):
    raw = await complete(system,prompt)
    return _parse_json_tolerant(raw)
