from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

INVENTORY_SERVICE_URL = "http://inventory:8000"
PAYMENT_SERVICE_URL = "http://payment:8000"

# Inventory service
@app.api_route("/inventory/{path:path}", methods=["GET", "POST", "DELETE"])
async def proxy_inventory(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{INVENTORY_SERVICE_URL}/{path}"

        response = await client.request(
            method = request.method,
            url = url,
            headers = request.headers.raw,
            content = await request.body()
        )

        return JSONResponse(
    content=response.json(),
    status_code=response.status_code
)
    
#  Payment Routes
@app.api_route("/payments/{path:path}", methods=["GET", "POST", "DELETE"])
async def proxy_payments(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        url = f"{PAYMENT_SERVICE_URL}/{path}"

        response = await client.request(
            method=request.method,
            url=url,
            headers=request.headers.raw,
            content=await request.body()
        )

        return JSONResponse(
        content=response.json(),
        status_code=response.status_code
        )