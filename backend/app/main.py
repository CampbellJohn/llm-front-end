from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.endpoints.openai_Router import router as api_router

app = FastAPI(
    title="LLM Chat API",
    description="API for interacting with various LLM providers",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the LLM Chat API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
