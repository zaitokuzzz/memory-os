# Memory OS

Adaptive modular memory operating system for AI with episodic, semantic, knowledge, behavior, and browser memory.

## Features
- Episodic memory
- Semantic memory
- Knowledge memory
- Behavior memory
- Browser evidence memory
- Retrieval orchestration
- Token-aware context packing
- Feedback loop
- Distillation
- Decay and archive workers

## Stack
- FastAPI
- PostgreSQL + pgvector
- Redis
- Celery
- Docker Compose

## Project Status
This project is under active development.

## Quick Start
1. Copy `.env.example` to `.env`
2. Start services with Docker Compose
3. Initialize database
4. Create vector indexes
5. Seed sample data
6. Open API docs

## Main Goal
Build a modular long-term memory backend for AI systems that reduces hallucination, improves context precision, and optimizes token usage.
