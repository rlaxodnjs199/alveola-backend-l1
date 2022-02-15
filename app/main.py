from fastapi import FastAPI
from app.api.v1.gapi.endpoints import gapi_router

app = FastAPI()
app.include_router(gapi_router)

@app.get("/")
async def hello():
    return {"Hello": "Google sheets API"}
