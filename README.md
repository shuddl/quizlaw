# QuizLaw

QuizLaw is a sophisticated legal MCQ generator application designed to help law students and legal professionals practice and master legal concepts through interactive quizzes.

## Features

- **Multiple Quiz Modes**: Random, Sequential, and Bar Prep (Law Student) modes
- **Interactive Quiz Interface**: Modern UI with immediate feedback
- **Detailed Explanations**: Get in-depth explanations for answers (Premium feature)
- **Customizable Quizzes**: Choose from different legal divisions and set the number of questions
- **Progress Tracking**: Monitor your performance over time (Premium feature)
- **User Authentication**: Create an account to save your progress
- **Premium Subscription**: Access advanced features with a premium subscription

## Technology Stack

- **Backend**: Python/Flask/SQLAlchemy
- **Frontend**: React/TypeScript/Tailwind CSS
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Payment Processing**: Stripe
- **Containerization**: Docker

## Local Development Setup

### Prerequisites

- Docker and Docker Compose
- Node.js (v16 or later)
- Python (v3.9 or later)
- Poetry (for Python dependency management)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Run the development server:
   ```bash
   poetry run flask run
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

### Using Docker Compose

You can also run the entire application stack using Docker Compose:

```bash
docker-compose up
```

This will start the backend, frontend, and PostgreSQL database.

## Database Migrations

To create a new migration:

```bash
cd backend
poetry run alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```bash
cd backend
poetry run alembic upgrade head
```

## Legal Data Scraping

To scrape legal sections from a division:

```bash
cd backend
poetry run python -m app.scripts.run_scraper <target_url>
```

## MCQ Generation

To generate MCQs for a division:

```bash
cd backend
poetry run python -m app.scripts.generate_mcqs <division_name> [num_per_section]
```

## Bar Relevance Update

To update bar-relevant sections:

```bash
cd backend
poetry run python -m scripts.update_bar_relevance <division> <file_path>
```

The file should contain one section number per line.

## Deployment

The application is configured for deployment to platforms like Render or Heroku using the included Dockerfiles and configuration files.

## License

This project is licensed under the MIT License - see the LICENSE file for details.