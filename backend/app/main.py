from fastapi import FastAPI
from fastapi import Depends
from app.security import verify_api_key
from fastapi.middleware.cors import CORSMiddleware

from app.routes import coins, prices, regression, correlation

app = FastAPI(
    title="Crypto Data Analysis API",
    description="Serves cached price history and regression results for BTC/ETH/SOL/BNB.",
    version="0.1.0",
)

# Dev-time CORS for the React frontend. Tighten this to your actual
# frontend origin before deploying anywhere public.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(coins.router, dependencies=[Depends(verify_api_key)])
app.include_router(prices.router, dependencies=[Depends(verify_api_key)])
app.include_router(regression.router, dependencies=[Depends(verify_api_key)])
app.include_router(correlation.router, dependencies=[Depends(verify_api_key)])


@app.get("/health")
def health():
    return {"status": "ok"}
