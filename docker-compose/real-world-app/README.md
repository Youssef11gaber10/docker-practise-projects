# Real-Life Application with Docker (Python + Redis + MySQL)

This is a sample application demonstrating how to containerize a Python Flask application with Redis and MySQL using Docker.

## Project Structure

```
real-life-app/
├── app/
│   └── app.py          # Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Python application container
└── docker-compose.yml # Multi-container orchestration
```

## Features

- Python Flask web application
- Redis for caching
- MySQL for persistent storage
- Docker containerization
- Docker Compose for orchestration

## How to Run

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone this repository and navigate to the project directory:
   ```bash
   cd real-life-app
   ```

3. Start the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. The application will be available at:
   - Web application: http://localhost:6000
   - Redis: localhost:6379
   - MySQL: localhost:3306

## API Endpoints

- `/` - Welcome message
- `/redis` - Test Redis connection
- `/mysql` - Test MySQL connection

## Environment Variables

The application uses the following environment variables:

- `REDIS_HOST` - Redis host (default: redis)
- `REDIS_PORT` - Redis port (default: 6379)
- `MYSQL_HOST` - MySQL host (default: mysql)
- `MYSQL_USER` - MySQL username (default: root)
- `MYSQL_PASSWORD` - MySQL password (default: password)
- `MYSQL_DATABASE` - MySQL database name (default: mydb)

## Stopping the Application

To stop the application and remove containers:
```bash
docker-compose down
```

To stop the application and remove containers and volumes:
```bash
docker-compose down -v
```