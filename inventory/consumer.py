from redis_client import redis, Product
import time

key = "order_completed"
group = "inventory-group"

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, None)
        if results:
            stream_name, messages = results[0]

            for message_id, obj in messages:
                try:
                    product = Product.get(obj["product_id"])
                    print(product)
                    product.quantity -= int(obj["quantity"])
                    product.save()
                except:
                    redis.xadd("refund_order", obj, "*")

     
    except Exception as e:
        print(str(e))
    time.sleep(1)