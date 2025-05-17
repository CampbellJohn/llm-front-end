# LLM Front-End Application

A containerized chat application with a React frontend and FastAPI backend, designed as a starting point to create a customized chat interface.

<center><img src="./llm-front-end-screenshot.png" alt="Screenshot of the application" width="600" /></center>

## Features

- React frontend with responsive design
- FastAPI backend
- Docker containerization for easy deployment
- Styled with Tailwind CSS

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/llm-front-end.git
cd llm-front-end
```

### 2. Set up environment variables

Create a `.env` file in the project root by editing .env.example:

```env
# Backend
OPENAI_API_KEY=your_openai_api_key_here

# Frontend (optional, for local development)
REACT_APP_API_URL=http://localhost:8000
```

### 3. Build and run with Docker

```bash
docker-compose up --build
```

This will:
1. Build the backend and frontend Docker images
2. Start both services
3. Make the application available at `http://localhost:3000`

### 4. Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs