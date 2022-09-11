from fastapi import APIRouter

from . import coins


INTERNAL_ROUTERS: list[APIRouter] = [module.router for module in [coins]]
