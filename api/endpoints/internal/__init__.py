from fastapi import APIRouter

from . import coins, premium


INTERNAL_ROUTERS: list[APIRouter] = [module.router for module in [coins, premium]]
