#!/bin/bash
uvicorn main:app --port 8000 --reload
python consumer.py
wait
