.DEFAULT_GOAL := help

ifeq ($(OS),Windows_NT)
PYTHON := .venv/Scripts/python.exe
else
PYTHON := .venv/bin/python
endif
PORT ?= 8000

.PHONY: help install run test check

help:
	@echo "Alvos: install, run, test, check"
	@echo "Crie primeiro a .venv. Execute os alvos na raiz do projeto."

install:
	"$(PYTHON)" -m pip install -r requirements.txt

run:
	"$(PYTHON)" -m uvicorn app.main:app --host 127.0.0.1 --port $(PORT)

test:
	"$(PYTHON)" -m pytest tests/test_tasks.py -v

check:
	"$(PYTHON)" -m pip check
