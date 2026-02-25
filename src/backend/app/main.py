

import uvicorn

from app.routers import all_routers
from app.service import create_app

app = create_app("Service Desk Backend")
for router in all_routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)
