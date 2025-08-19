from typing import Union
import uvicorn
from fastapi import FastAPI
from qes_types.res import QueryModel
from config import open_client
from routers.chat_router import router as chat_router

app = FastAPI()

app.include_router(chat_router, prefix="/chat", tags=["chat"])

@app.get("/")
def read_root():
    return "QES Agent"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9010)
