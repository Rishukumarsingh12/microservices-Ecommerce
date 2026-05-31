from redis_client import redis, Product
import time

key = "order_completed"
group = "inventory-group"

try:
    redis.xgroup_create(key, group, id="0", mkstream=True)
except Exception:
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
                    if product.quantity < int(obj["quantity"]):
                        print("Not enough inventory, refunding order")
                        redis.xadd("refund_order", obj, "*")
                        redis.xack(
                            key,
                            group,
                            message_id
                        )
                        continue
                    else:
                        product.quantity -= int(obj["quantity"])
                        product.save()
                        redis.xack(
                            key,
                            group,
                            message_id
                        )

                except Exception as e:

                    print(f"Processing error: {str(e)}")

                    redis.xadd(
                        "refund_order",
                        obj,
                        "*"
                    )

                    redis.xack(
                        key,
                        group,
                        message_id
                    )

     
    except Exception as e:
        print(f"Inventory consumer error: {str(e)}")

    time.sleep(1)