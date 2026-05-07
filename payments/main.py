from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from redis_client import Order,redis
import requests, time
from fastapi.background import BackgroundTasks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/orders")
def get_orders():
    return [format(order) for order in Order.all_pks()]

def format(pk:str):
    order = Order.get(pk)
    return {
        "order_id":order.pk,
        "product_id":order.product_id,
        "order_price":order.price,
        "order_fee":order.fee,
        "order_total":order.total,
        "order_quantity":order.quantity,
        "order_status":order.status
    }

@app.get("/orders/{pk}")
def get_order(pk: str):
    order = Order.get(pk)
    return order

@app.delete("/delete_orders/{pk}")
def delete_order(pk: str):
    order =Order.get(pk)
    order.delete()
    return {"message":"Order deleted successfully"}

@app.post("/orders")
async def create_order(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()

    product = requests.get("http://inventory:8000/get_products/%s" % body["id"]).json()

    order = Order(
        product_id = body["id"],
        price = product["price"],
        fee = round(product["price"] * 0.2 * body["quantity"], 2),
        total = round(product["price"] * 1.2 * body["quantity"], 2),
        quantity = body["quantity"],
        status = "pending"
    )

    order.save()
    #This is how background function run in FastAPI. any argument passed to the function will be written after the function name in add_task. 
    #This is a non-blocking call, so the function will run in the background while the main thread continues to execute.

    background_tasks.add_task(update_order_status, order)
    
    return order
"""
def update_order_status(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()
    redis.xadd("order_completed", order.dict(), "*")"""
def update_order_status(order: Order):
    try:
        time.sleep(5)

        order = Order.get(order.pk)  # reload latest state

        if order.status != "pending":
            return  # already refunded → don't override

        response = requests.get(f"http://inventory:8000/get_products/{order.product_id}")

        if response.status_code != 200:
            order.status = "refunded"
            redis.xadd('order_refunded', order.dict(), '*')
        else:
            order.status = "completed"
            redis.xadd('order_completed', order.dict(), '*')

        order.save()
    except Exception as e:
        print("Error:", str(e))
# How do we update the quantity of the products after any order is successfully placed?
"""
Redis stream functionality allow us to communicate between different microservices by sending events 
and they won't know about each other.
"""

