from fastapi import APIRouter
from app.api.endpoints import products, transactions, forecasts, recommendations, auth

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(transactions.router)
api_router.include_router(forecasts.router)
api_router.include_router(recommendations.router)
