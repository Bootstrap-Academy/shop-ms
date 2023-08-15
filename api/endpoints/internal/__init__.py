from fastapi import APIRouter

from . import coins, hearts, premium


INTERNAL_ROUTERS: list[APIRouter] = [module.router for module in [coins, premium, hearts]]
