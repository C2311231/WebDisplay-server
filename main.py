"""
Webdisplay Server
Entrypoint

License: MIT license

Author: C2311231

Notes:
"""


from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import src.endpoints.api as api

app = FastAPI()
app.include_router(api.router)

class DeviceRegistration(BaseModel):
    device_id: str
    device_name: str
    device_type: str

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )