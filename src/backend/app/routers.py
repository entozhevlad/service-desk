from app.api.healthz.handler import health_router
from app.api.tickets.handler import tickets_router

all_routers = [health_router, tickets_router]
