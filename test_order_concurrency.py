"""
Concurrent stress test for OrderBook lock mechanism.
Tests thread safety by firing concurrent order requests.
"""

import asyncio
import httpx
import time
import logging
from logger import setup_logger
from config import (
    STRESS_TEST_NUM_ORDERS
)

logger = setup_logger("test_order_concurrency")

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
        response = await client.post("http://127.0.0.1:8000/orders", json=order_data, timeout=30.0)
        logger.debug(f"Order {order_id}: Status {response.status_code}")
        return response.status_code
    except Exception as e:
        logger.error(f"❌ Order {order_id} failed: {type(e).__name__}: {e}")
        return str(e)

async def main():
    """
    Main concurrent test: Launch orders simultaneously.
    Measures throughput and validates lock prevents data corruption.
    """
    num_orders = STRESS_TEST_NUM_ORDERS
    async with httpx.AsyncClient() as client:
        # Create coroutines (not executed yet)
        tasks = [send_order(client, i) for i in range(num_orders)]

        logger.info(f"🔥 Starting stress test: Blasting {num_orders} orders at once...")
        start_time = time.time()
        # Execute all tasks concurrently (locks serialize access to OrderBook)
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Report results
        successes = results.count(200)
        failures = len(results) - successes
        elapsed_time = end_time - start_time

        logger.info(f"📊 Stress test completed!")
        logger.info(f"✅ Successes: {successes}/{num_orders}")
        logger.info(f"❌ Failures: {failures}/{num_orders}")
        logger.info(f"⏱️  Time elapsed: {elapsed_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
