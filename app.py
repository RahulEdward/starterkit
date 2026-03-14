"""
Best-Option - Local-First Options Trading Analytics Desktop Application
FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers (FastAPI mein blueprints ko routers kehte hain)
from routes.auth import router as auth_router
from routes.market import router as market_router
from routes.orders import router as orders_router
from routes.positions import router as positions_router
from routes.master_contract import router as master_contract_router
from routes.search import router as search_router
from routes.search import router as search_router

# Initialize databases
from database.user_db import init_db as init_user_db
from database.auth_db import init_db as init_auth_db
from database.symbol import init_db as init_symbol_db
from database.master_contract_status_db import init_db as init_master_contract_status_db

app = FastAPI(
    title="Best-Option API",
    description="High-performance options trading analytics for NSE/BSE markets",
    version="1.0.0"
)

# CORS middleware for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize databases on startup
@app.on_event("startup")
async def startup_event():
    init_user_db()
    init_auth_db()
    init_symbol_db()
    init_master_contract_status_db()
    print("✅ Databases initialized")

# Include routers (Flask ke app.register_blueprint() jaisa)
app.include_router(auth_router)
app.include_router(market_router)
app.include_router(orders_router)
app.include_router(positions_router)
app.include_router(master_contract_router)
app.include_router(search_router)
app.include_router(search_router)

@app.get("/")
async def root():
    return {"message": "Best-Option API is running", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
