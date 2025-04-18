# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands

- Backend setup: `cd backend && poetry install`
- Frontend setup: `cd frontend && npm install`
- Backend dev server: `cd backend && poetry run flask run`
- Frontend dev server: `cd frontend && npm run dev`
- Backend tests: `cd backend && poetry run pytest`
- Single test: `cd backend && poetry run pytest path/to/test_file.py::test_function`
- Backend lint: `cd backend && poetry run ruff check app`
- Frontend lint: `cd frontend && npm run lint`
- Typecheck: `cd backend && poetry run mypy app`

## Code Style Guidelines

- Backend: Python with strict typing, Black formatting, Ruff linting
- Frontend: TypeScript, ESLint, Prettier
- UI design: Black & White base with #ff0000 red accent
- Imports: Absolute imports, organized by stdlib/third-party/local
- Variable naming: camelCase for JS/TS, snake_case for Python
- Error handling: Try/except with specific exception types
- Component structure: Functional React components with hooks
- Testing: pytest for backend, React Testing Library for frontend