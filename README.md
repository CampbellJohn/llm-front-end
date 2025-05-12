# LLM Front End
This project will act as a starting front-end to an LLM. It will be configured to connect to OpenAI, but will eventually be extended to connect to other LLMs.
The back-end of this project will be a Docker container running a FastAPI python project.
The front-end will connect from a docker container running a react UI.

llm-chat-app/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile.backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── __init__.py
│   │   │       │   └── openai_router.py
│   │   │       └── models/
│   │   │           ├── __init__.py
│   │   │           └── openai_models.py
│   │   ├── utilities/
│   │   │   └── __init__.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── openai_service.py
│   └── requirements.txt
└── frontend/
    ├── Dockerfile.frontend
    ├── package.json
    ├── public/
    │   ├── index.html
    │   └── favicon.ico
    └── src/
        ├── App.js
        ├── index.js
        ├── components/
        │   ├── ChatInterface.jsx
        │   ├── ChatMessage.jsx
        │   ├── MessageInput.jsx
        │   └── ModelSelector.jsx
        ├── services/
        │   └── api.js
        ├── hooks/
        │   └── useChat.js
        └── styles/
            └── main.css


#Favicon Temp Reference
Extract this package in <your app>/public/.
In <your app>/public/index.html, remove the existing link markups (they have have attributes rel="icon", rel="apple-touch-icon" and rel="manifest").
Insert the following code in the head section of <your app>/public/index.html:

<link rel="icon" type="image/png" href="%PUBLIC_URL%/favicon-96x96.png" sizes="96x96" />
<link rel="icon" type="image/svg+xml" href="%PUBLIC_URL%/favicon.svg" />
<link rel="shortcut icon" href="%PUBLIC_URL%/favicon.ico" />
<link rel="apple-touch-icon" sizes="180x180" href="%PUBLIC_URL%/apple-touch-icon.png" />
<link rel="manifest" href="%PUBLIC_URL%/site.webmanifest" />