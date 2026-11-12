#!/bin/bash
export FORCE_DEMO=1
uvicorn atlas.app.main:app --host 0.0.0.0 --port 8000