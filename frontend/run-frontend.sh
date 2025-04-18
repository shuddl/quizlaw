#!/bin/bash
echo "Starting QuizLaw frontend directly on port 3000..."
export VITE_API_URL=http://localhost:5000
npm run dev -- --port 3000 --host

