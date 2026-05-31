from redis_client import redis, Order
import time

key = "refund_order"
group = "payment-group"

try:
    redis.xgroup_create(key, group, id="0", mkstream=True)
except Exception:
    print("Group already exists")
while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, None)
        print("results:",results)
        if results:
            stream_name, messages = results[0]

            for message_id, obj in messages:
                print("EVENT:", obj)

                orders = Order.find(Order.product_id == obj["product_id"]).all()

                for order in orders:
                    if order.status == "pending":
                        order.status = "refunded"
                        order.save()
                        print("REFUNDED:", order.dict())
                redis.xack(key, group, message_id)

    except Exception as e:
        print(f"Refund processing error: {str(e)}")

    time.sleep(1)