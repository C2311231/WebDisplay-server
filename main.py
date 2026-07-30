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

app = FastAPI()

class DeviceRegistration(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    
    
devices = []

@app.post("/register-device")
async def register_device(device: DeviceRegistration):
    devices.append(device)
    print(f"Registered device: {device.device_id}, {device.device_name}, {device.device_type}")
    return {"message": "Device registered successfully"}



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )