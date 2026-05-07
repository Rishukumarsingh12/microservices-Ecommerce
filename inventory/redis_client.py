from dotenv import load_dotenv
import os
from redis_om import get_redis_connection,HashModel

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")



redis = get_redis_connection(
    host=REDIS_URL,
    port = REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

class Product(HashModel, index=True):
    name:str
    price:float
    quantity:int

    class Meta:
        database = redis