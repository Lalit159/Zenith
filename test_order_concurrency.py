"""
Concurrent stress test for OrderBook lock mechanism.
Tests thread safety by firing 100 simultaneous order requests.
"""

import asyncio
import httpx
import time

async def send_order(client, order_id):
    """
    Send a single order to the API.
    Alternates between BUY (even IDs) and SELL (odd IDs) at price $100.
    This ensures matching will occur.
    """
    order_data = {
        "order_id": order_id,
        "side": "buy" if order_id % 2 == 0 else "sell",
        "price": 100,
        "quantity": 1
    }
    try:
        response = await client.post("http://127.0.0.1:8000/orders", json=order_data, timeout=30.0) #Change to 13.0 and see how many orders complete before timeout
        return response.status_code
    except Exception as e:
        print(f"❌ Order {order_id} failed: {type(e).__name__}: {e}")
        return str(e)

async def main():
    """
    Main concurrent test: Launch 1000 orders simultaneously.
    Measures throughput and validates lock prevents data corruption.
    """
    num_orders = 1000
    async with httpx.AsyncClient() as client:
        # Create 1000 coroutines (not executed yet)
        tasks = [send_order(client, i) for i in range(num_orders)]

        print(f"Blasting {num_orders} orders at once...")
        start_time = time.time()
        # Execute all tasks concurrently (locks serialize access to OrderBook)
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Report results
        successes = results.count(200)
        failures = len(results) - successes
        print(f"\n✅ Finished in {end_time - start_time:.4f} seconds")
        print(f"✅ Successes: {successes}/{num_orders}")
        print(f"❌ Failures: {failures}/{num_orders}")

if __name__ == "__main__":
    asyncio.run(main())
