from fastapi import FastAPI,HTTPException
#from redis.exceptions import NotFoundError
from fastapi.middleware.cors import CORSMiddleware
from redis_client import redis, Product
from redis_om.model.model import NotFoundError
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)



@app.get("/products")
def get_products():
    try:
        return [format(pk) for pk in Product.all_pks()]
    except NotFoundError:
        raise HTTPException(status_code=404, detail="No products available in inventory") 

def format(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }

@app.post("/create_products")
def create_products(products: Product):
    return products.save()

@app.delete("/delete_products/{pk}")
def delete_product(pk: str):
    try:
        product = Product.get(pk)
    
        # Emit refund event
        redis.xadd("refund_order", product.dict(), "*")

        Product.delete(pk)

        return {"message": "Product deleted"}
    except NotFoundError:
        raise HTTPException(status_code = 404,
                            detail = "Product is not available")

@app.get("/get_products/{pk}")
def get_product(pk: str):
    try:
        return Product.get(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
   