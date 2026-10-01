from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, community, chatbot, mall, blockchain

app = FastAPI(
    title="K-Enterprise 4-Tier Hybrid Backend API",
    description="Community · AI ChatBot · Closed Mall · Blockchain 4-Tier Core API Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (DMZ Security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(community.router, prefix="/api/v1")
app.include_router(chatbot.router, prefix="/api/v1")
app.include_router(mall.router, prefix="/api/v1")
app.include_router(blockchain.router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "healthy",
        "service": "K-Enterprise 4-Tier Hybrid Core",
        "protocol": "HTTPS / WSS / JSON-RPC",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
