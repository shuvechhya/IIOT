import os
import platform
import subprocess
from subprocess import PIPE

import httpx
import psutil

# import uvicorn
from bson import ObjectId
from configuration import user_col
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NetworkConnect(BaseModel):
    ssid: str
    password: str


class AuthRequest(BaseModel):
    email: str
    password: str


class AuthzRequest(BaseModel):
    username: str
    action: str
    topic: str


class SSIDType(BaseModel):
    ssid: str
    signal: str
    security: str


@app.get("/ipaddress")
async def getIpAddress():
    addresses = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family.name == "AF_INET":  # IPv4 only
                addresses.append({"name": iface, "ip": addr.address})
    return addresses


@app.get("/connected/network")
async def getConnectedNetwork():
    os_type = platform.system()
    ssid = ""

    try:
        if os_type == "Linux":
            result = subprocess.run(
                ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            for line in output.splitlines():
                active, ssid_name = line.split(":")
                if active == "yes":
                    ssid = ssid_name.strip()
                    break

        else:
            print(f"Unsupported OS: {os_type}")

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")

    return ssid


@app.get("/network")
async def getNetwork():
    os_type = platform.system()
    output = ""
    ssids: list[SSIDType] = []

    if os_type == "Linux":
        try:
            process = subprocess.Popen(
                [
                    "nmcli",
                    "-t",
                    "-f",
                    "SSID,SIGNAL,SECURITY",
                    "dev",
                    "wifi",
                    "list",
                    "--rescan",
                    "yes",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                shell=False,
            )
            stdout, stderr = process.communicate()
            output = stdout
            print("Linux Networks found:")
            print(output)
            for line in output.splitlines():
                parts = line.split(":")
                if len(parts) >= 3:
                    ssid, signal, security = (
                        parts[0].strip(),
                        parts[1].strip(),
                        parts[2].strip(),
                    )
                    if ssid and ssid != "--":
                        ssids.append(
                            SSIDType(ssid=ssid, signal=signal, security=security)
                        )
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=f"Internal Error: {e}")

    else:
        print(f"Unsupported OS: {os_type}")
        return []

    return {"output": ssids}


@app.post("/network")
async def connectWifi(network: NetworkConnect):
    print(f"Attempting to connect to {network.ssid}...")

    os_name = platform.system()

    try:
        if os_name == "Linux":
            cmd = [
                "nmcli",
                "dev",
                "wifi",
                "connect",
                network.ssid,
                "password",
                network.password,
            ]
            subprocess.run(cmd, check=True)

        else:
            print(f"Unsupported OS: {os_name}")
            return "error"

        print(f"Successfully connected to {network.ssid}")
        return "success"

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")


@app.post("/auth")
async def authenticate(auth: AuthRequest):
    iiot_dashboard = os.getenv("IIOT_DASHBOARD_IP", "localhost")
    dashboard_port = os.getenv("IIOT_DASHBOARD_PORT", 5173)
    external_validation_url = (
        f"http://{iiot_dashboard}:{dashboard_port}/api/auth/sign-in/email"
    )
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                external_validation_url,
                json={"email": auth.email, "password": auth.password},
            )
            print(response)
            response.raise_for_status()

            return {"result": "allow"}

        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=401, detail="Authentication failed with external service"
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=503, detail="Cannot reach external authentication service"
            )


@app.post("/authorize")
async def http_authorize(authz: AuthzRequest):
    user = authz.username
    db_user = user_col.find_one({"email": user})
    topic_owner_id = authz.topic.split("/")[0]

    print(authz)
    print(db_user)
    print(f"Topic owner ID extracted: {topic_owner_id}")

    if db_user:
        if db_user.get("role") == "admin":
            if topic_owner_id == "" or topic_owner_id == "#":
                return {"result": "allow"}

        try:
            topic_owner_object_id = ObjectId(topic_owner_id)
            if db_user["_id"] == topic_owner_object_id:
                if authz.action in ["publish", "subscribe"]:
                    return {"result": "allow"}
        except Exception:
            pass

        if authz.topic.startswith("$SYS"):
            return {"result": "ignore"}

        return {"result": "deny"}
    else:
        return {"result": "deny"}


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",  # The module:app string, or the app object itself
#         host="192.168.1.35",
#         port=8600,
#         reload=True,  # Optional: use for development
#     )
