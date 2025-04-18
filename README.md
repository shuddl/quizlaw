# QuizLaw

QuizLaw is a sophisticated legal MCQ generator application designed to help law students and legal professionals practice and master legal concepts through interactive quizzes.

![QuizLaw Banner](https://via.placeholder.com/1200x300/0A2647/FFFFFF?text=QuizLaw:+Master+Legal+Concepts)

## Features

### Core Features

- **Multiple Quiz Modes**:
  - *Random Mode*: Test your knowledge with random questions across selected divisions
  - *Sequential Mode*: Study methodically by following the legal code's structure
  - *Bar Prep (Law Student) Mode*: Focus exclusively on sections relevant to the bar exam
- **Interactive Quiz Interface**: Modern UI with immediate feedback on answers
- **Detailed Explanations**: Get in-depth explanations for answers (Premium feature)
- **Customizable Quizzes**: Choose from different legal divisions and set the number of questions
- **Dynamic Legal References**: Each question links back to the original legal code section

### Premium Features

- **Answer Explanations**: Understand why answers are correct or incorrect
- **Progress Tracking**: Monitor your performance over time with detailed analytics
- **Performance Dashboards**: Visual representation of your strengths and weaknesses
- **Learning Paths**: AI-generated study recommendations based on your performance
- **Export Functionality**: Download question sets or quiz results in various formats

## Technology Stack

- **Backend**: Python/Flask/SQLAlchemy with async support
- **Frontend**: React/TypeScript with Tailwind CSS
- **Database**: PostgreSQL for robust data storage
- **API**: RESTful API with comprehensive documentation
- **Authentication**: Secure JWT-based authentication
- **Payment Processing**: Stripe integration for subscription and one-time payments
- **Containerization**: Docker and Docker Compose for consistent environments
- **AI Integration**: OpenAI GPT-4 for MCQ generation

## Local Development Setup

### Prerequisites

- Docker and Docker Compose
- Node.js (v16 or later)
- Python (v3.9 or later)
- Poetry (for Python dependency management)
- PostgreSQL (optional, can use containerized version)

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

4. Generate a secure Flask secret key:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Add the generated key to your `.env` file:

   ```
   SECRET_KEY=your_generated_key_here
   ```

6. Run the development server:

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

3. Create a `.env` file for frontend configuration:

   ```bash
   cp .env.example .env
   ```

4. Set the API URL in the `.env` file:

   ```
   VITE_API_BASE_URL=http://localhost:5000/api/v1
   ```

5. Run the development server:

   ```bash
   npm run dev
   ```

### Using Docker Compose

You can also run the entire application stack using Docker Compose:

```bash
docker-compose up
```

This will start the backend, frontend, and PostgreSQL database services together.

To rebuild containers after making changes:

```bash
docker-compose build
docker-compose up
```

For production mode:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Environment Variables

### Critical Backend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key for secure sessions | `b'your-generated-key'` |
| DATABASE_URL | PostgreSQL database connection string | `postgresql+asyncpg://user:password@localhost/quizlaw` |
| OPENAI_API_KEY | OpenAI API key for MCQ generation | `sk-...` |
| JWT_SECRET_KEY | Secret key for JWT token generation | `your-jwt-secret` |
| STRIPE_API_KEY | Stripe API key for payment processing | `sk_test_...` |

### Critical Frontend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| VITE_API_BASE_URL | Base URL for backend API | `http://localhost:5000/api/v1` |
| VITE_STRIPE_PUBLIC_KEY | Stripe publishable key | `pk_test_...` |

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

To revert the most recent migration:

```bash
cd backend
poetry run alembic downgrade -1
```

## Legal Data Scraping

QuizLaw includes a sophisticated scraper system for extracting legal code from public websites.

### Basic Scraping

To scrape legal sections from a division:

```bash
cd backend
poetry run python -m app.scripts.run_scraper <target_url>
```

### Enhanced Scraping

The enhanced scraper provides more options and better handling of complex legal documents:

```bash
cd backend
poetry run python -m scripts.enhanced_scraper --url <target_url>
```

#### Advanced Scraping Options:

- **Scrape multiple divisions at once**:

  ```bash
  poetry run python -m scripts.enhanced_scraper --urls <url1> <url2> <url3>
  ```

- **Adjust concurrent requests** for faster scraping:

  ```bash
  poetry run python -m scripts.enhanced_scraper --url <target_url> --concurrency 5
  ```

The enhanced scraper can handle:
- Complex document structures
- Multi-part sections and subsections
- Footnotes and annotations
- Various website layouts and formatting styles

## MCQ Generation

To generate MCQs for all sections in a division:

```bash
cd backend
poetry run python -m app.scripts.generate_mcqs <division_name> [num_per_section]
```

To regenerate MCQs for specific sections:

```bash
cd backend
poetry run python -m app.scripts.regenerate_mcqs --section-ids <id1> <id2> <id3>
```

## Bar Relevance Update

To update bar-relevant sections from a text file:

```bash
cd backend
poetry run python -m scripts.update_bar_relevance <division> <file_path>
```

The file should contain one section number per line.

To mark individual sections as bar-relevant:

```bash
cd backend
poetry run python -m scripts.mark_bar_relevant <section_number1> <section_number2> ...
```

## Monetization Features

QuizLaw offers multiple monetization channels:

### 1. Premium Subscription Tiers

- **Basic Plan**: Access to standard quizzes
- **Pro Plan**: Includes answer explanations and basic analytics
- **Enterprise Plan**: Full analytics suite, custom question sets, and API access

To configure subscription plans:

```bash
cd backend
poetry run python -m scripts.update_subscription_plans
```

### 2. Advertising Integration

QuizLaw supports Google AdSense and custom advertising solutions:

- Configure ad placements in `/frontend/src/components/AdBanner.tsx`
- Manage ad settings in the admin panel
- A/B test different ad formats for optimal performance

### 3. Affiliate Programs (Future Implementation)

QuizLaw's planned affiliate program features include:

#### Affiliate Dashboard

- Track referrals, conversions, and earnings
- Generate unique referral links
- Access promotional materials

#### Integration with Legal Resource Providers

- Law textbook publishers
- Legal research platforms
- Bar preparation courses

#### Commission Structure

- Tiered commission rates based on referral volume
- Recurring commissions for subscription referrals
- Bonus incentives for high-performing affiliates

#### Implementation Roadmap

1. **Phase 1 (Q3 2025)**
   - Affiliate tracking system
   - Basic dashboard and referral links
   - First-tier partnerships with 2-3 legal publishers

2. **Phase 2 (Q4 2025)**
   - Enhanced analytics for affiliates
   - API for affiliate partners
   - Expanded partner network

3. **Phase 3 (Q1 2026)**
   - Marketplace for legal resources
   - White-label solutions for institutional partners
   - Advanced commission structures

#### Affiliate Program Technical Architecture

The affiliate system will be built on:
- Event-based tracking via a dedicated tracking service
- Secure attribution with fraud prevention measures
- RESTful API for partner integrations
- Dashboard built with React and D3.js for analytics visualization

## Deployment

### Preparing for Deployment

1. Generate a secure Flask secret key:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. Set up environment variables on your hosting platform:
   - SECRET_KEY (use the generated key)
   - DATABASE_URL
   - OPENAI_API_KEY
   - JWT_SECRET_KEY
   - STRIPE_API_KEY
   - Other configuration variables

### Deployment Options

#### Using the Deployment Scripts

The project includes deployment scripts for both frontend and backend:

```bash
# Deploy everything
./deploy.sh --all --env prod --build --push

# Deploy only backend
./deploy.sh --backend --env prod

# Deploy only frontend
./deploy.sh --frontend --env prod
```

#### Platform-Specific Deployments

**Render**:
- Connect your GitHub repository
- Configure build settings according to render.yaml
- Set up required environment variables

**Heroku**:
- Use the included Procfile
- Configure PostgreSQL add-on
- Set environment variables in the dashboard

**AWS/Digital Ocean**:
- Use Docker Compose with the production configuration
- Configure a reverse proxy (Nginx/Traefik)
- Set up SSL certificates

### Database Backups

Configure regular database backups:

```bash
# Set up a cron job for daily backups
0 0 * * * /path/to/quizlaw/scripts/backup_database.sh
```

## Testing

Run backend tests:

```bash
cd backend
poetry run pytest
```

Run frontend tests:

```bash
cd frontend
npm test
```

## API Documentation

API documentation is available at `/api/docs` when the server is running.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for providing the GPT-4 API
- The open source community for the amazing tools and libraries
- Legal scholars who contributed to the validation of questions