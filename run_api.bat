@echo off
call venv\Scripts\activate
uvicorn api:app --reload --port 8000
