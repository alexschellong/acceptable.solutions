from fastapi import FastAPI
import uvicorn
from new_request_endpoint.new_request import router

# Create FastAPI instance
app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000)

