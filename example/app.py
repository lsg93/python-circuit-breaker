from fastapi import FastAPI

from example.api import router

app = FastAPI()
app.include_router(router)


@app.get("/gateway")
def gateway_call():
    pass
