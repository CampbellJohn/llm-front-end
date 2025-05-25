# LLM Front-End Application

A containerized chat application with a React frontend and FastAPI backend, designed as a starting point to create a customized chat interface.

<center>
  <img src="./llm-front-end-screenshot.png" alt="Screenshot" width="800" />
</center>

## Features

- **React Frontend**
  - Responsive design with Tailwind CSS
  - Conversation history and management
  - Clean, intuitive interface

- **FastAPI Backend**
  - RESTful API ready for extension
  - MongoDB integration for persistent storage
  - Asynchronous request handling

- **Deployment**
  - Docker containerization utilizing docker compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Node.js and npm (for local development)

### 1. Clone the repository

```bash
git clone https://github.com/CampbellJohn/llm-front-end.git
cd llm-front-end
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB
MONGODB_URL=mongodb://mongodb:27017/llm_chat_db
MONGODB_DB_NAME=llm_chat_db
```

### 3. Run Tests (Optional)

Frontend testing happens automatically when the container starts. Backend testing can be run in its own container:

```bash
docker-compose --profile test build --no-cache backend-test
docker-compose --profile test run --rm backend-test
```

This command:
- Uses the test profile to include the test service
- Runs the tests in the test environment
- Automatically removes the test container when done (`--rm` flag)
- Exits with a non-zero code if tests fail

### 4. Start the Docker containers

```bash
docker-compose up --build
```

This will start:
- MongoDB container
- FastAPI backend
- React frontend

### 5. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
llm-front-end/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/    # API route handlers
│   │   │       └── models/       # Pydantic models
│   │   ├── core/                # Core configurations
│   │   └── services/            # Business logic
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API service functions
│   │   └── App.js              # Main application component
│   └── package.json
├── .env.example
├── docker-compose.yml
└── README.md
```