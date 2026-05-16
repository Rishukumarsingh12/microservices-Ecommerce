from fastapi import FastAPI,Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv
import os

from jose import jwt, JWTError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

app = FastAPI()

INVENTORY_SERVICE_URL = "http://inventory:8000"
PAYMENT_SERVICE_URL = "http://payment:8000"
AUTH_SERVICE_URL = "http://auth:8000"

def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code = 401,
            detail = "Authorization header missing"
        )
    
    try:
        token = auth_header.split(" ")[1]

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms = [ALGORITHM]
        )

        return payload
    except JWTError:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )
    
# Inventory service
@app.api_route("/inventory/{path:path}", methods=["GET", "POST", "DELETE"])
async def proxy_inventory(request: Request, path: str):
    
    verify_token(request)

    async with httpx.AsyncClient() as client:
        url = f"{INVENTORY_SERVICE_URL}/{path}"

        response = await client.request(
            method = request.method,
            url = url,
            headers = request.headers.raw,
            content = await request.body()
        )
        try:
            content = response.json()
        except:
            content = {"detail": response.text}

        return JSONResponse(
            content=content,
            status_code=response.status_code
        )
    
#  Payment Routes
@app.api_route("/payments/{path:path}", methods=["GET", "POST", "DELETE"])
async def proxy_payments(path: str, request: Request):

    verify_token(request)

    async with httpx.AsyncClient() as client:
        url = f"{PAYMENT_SERVICE_URL}/{path}"

        response = await client.request(
            method=request.method,
            url=url,
            headers=request.headers.raw,
            content=await request.body()
        )
        try:
            content = response.json()
        except:
            content = {"detail": response.text}

        return JSONResponse(
        content=content,
        status_code=response.status_code
        )
    
@app.api_route("/auth/{path:path}", methods=["POST"])
async def proxy_auth(request: Request, path: str):

    async with httpx.AsyncClient() as client:
        url = f"{AUTH_SERVICE_URL}/{path}"

        response = await client.request(
            method = request.method,
            url = url,
            headers = request.headers.raw,
            content = await request.body()
        )

        try:
            content = response.json()
        except:
            content = {"detail": response.text}

        return JSONResponse(
    content=content,
    status_code=response.status_code
)