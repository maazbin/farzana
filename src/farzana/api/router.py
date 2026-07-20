"""Aggregate API routers."""

from fastapi import APIRouter

from farzana.api.routes import admin, health, telegram

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(telegram.router)
api_router.include_router(admin.router)
