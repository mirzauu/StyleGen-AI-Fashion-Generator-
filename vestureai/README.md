# VestureAI

VestureAI is an AI-driven image generation platform designed for branded garment visualization using human model photos. This project leverages FastAPI for building a robust API, PostgreSQL for data storage, and Celery for asynchronous processing of image generation tasks.

## Project Structure

```
vestureai
├── app
│   ├── main.py                # Entry point of the FastAPI application
│   ├── core                    # Core functionalities (auth, config, utils)
│   ├── models                  # SQLAlchemy models for database entities
│   ├── api                     # API routers for handling requests
│   ├── services                # Business logic and external service integrations
│   ├── workers                 # Celery tasks for background processing
│   ├── schemas                 # Pydantic models for data validation
│   └── tests                   # Unit tests for the application
├── alembic                     # Database migration scripts and configurations
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Features

- **User Authentication**: Secure registration and login functionalities.
- **Subscription Management**: Users can choose from various subscription plans and manage their subscriptions.
- **Model Catalog**: Browse and retrieve details about available models.
- **Task Management**: Create tasks for garment image uploads and manage batches for image generation.
- **Asynchronous Image Generation**: Offload image generation tasks using Celery for better performance.
- **File Storage**: Manage image uploads and retrievals using S3 or MinIO.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Redis (for Celery)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd vestureai
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   - Create a PostgreSQL database and update the connection details in `app/core/config.py`.

4. Run database migrations:
   ```
   alembic upgrade head
   ```

5. Start the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

6. Start the Celery worker:
   ```
   celery -A app.workers.image_tasks worker --loglevel=info
   ```

## API Documentation

The API documentation is automatically generated and can be accessed at `http://localhost:8000/docs` after starting the FastAPI application.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.