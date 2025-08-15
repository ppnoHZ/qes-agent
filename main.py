from typing import Union
import uvicorn
from fastapi import FastAPI
from qes_types.res import QueryModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/suggestion')
def suggestion(query: QueryModel):
    return 'QueryModel'

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9009)

