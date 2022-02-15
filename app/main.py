from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.gapi.endpoints import gapi_router

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app = FastAPI()
app.include_router(gapi_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def hello():
    return {"Hello": "Google sheets API"}
