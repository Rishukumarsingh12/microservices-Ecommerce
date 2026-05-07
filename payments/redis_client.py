from dotenv import load_dotenv
import os
from redis_om import get_redis_connection,HashModel

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


#This should be a different db instance than Product.
redis = get_redis_connection(
    host=REDIS_URL,
    port = REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

class Order(HashModel, index=True):
    product_id:str
    price:float
    fee:float
    total:float
    quantity:int
    status:str

    class Meta:
        database = redis

