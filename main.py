from fastapi import FastAPI
from app.views import router

# Initialize FastAPI app
app = FastAPI()

route_prefix = "/advait-assignment/v1"

# Include API router from views
app.include_router(router, prefix=route_prefix)