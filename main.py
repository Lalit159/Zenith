# Creating Zenith - Real-time order matching engine

import logging
from fastapi import FastAPI, HTTPException
from models import Order, OrderRequest
from order_book import OrderBook
from logger import setup_logger

logger = setup_logger(__name__)


# NOTE: FastAPI concurrency model:
# - def → runs in threadpool (blocking, separate thread)
# - async def → runs in event loop (non-blocking, single thread via await)
# - Our OrderBook is CPU-bound (in-memory), so no I/O bottleneck.
# - If adding database/API calls, use async/await to avoid blocking event loop.

app = FastAPI()
order_book = OrderBook()

@app.get("/")
async def root():
    logger.debug("GET / - Root endpoint accessed")
    return {"message": "Welcome to Zenith - Real-time Order Matching Engine!"}


@app.post("/orders")
async def create_order(order_request: OrderRequest):
    logger.debug(f"POST /orders - Received order request: {order_request}")

    if order_request.order_id in order_book.orders_map:
        logger.error(f"Order ID {order_request.order_id} already exists")
        raise HTTPException(status_code=400, detail="Order ID already exists.")

    order = Order(order_request.order_id, order_request.side, order_request.price, order_request.quantity)
    logger.info(f"✅ Creating new order: {order}")

    await order_book.add_order(order)
    return {"message": "Order added successfully."}


@app.delete("/orders/{order_id}")
async def cancel_order(order_id: int):
    logger.debug(f"DELETE /orders/{order_id} - Received cancellation request")

    if order_id not in order_book.orders_map:
        logger.error(f"Attempted to cancel non-existent order {order_id}")
        raise HTTPException(status_code=404, detail="Order ID not found.")

    logger.info(f"🗑️  Cancelling order {order_id}")
    await order_book.cancel_order(order_id)
    return {"message": "Order cancelled successfully."}


@app.get("/book")
async def get_order_book():
    logger.debug("GET /book - Retrieving order book snapshot")
    async with order_book.lock:
        bid_count = len([o for o in order_book.bids if not o[2].is_cancelled])
        ask_count = len([o for o in order_book.asks if not o[2].is_cancelled])
        logger.debug(f"Order book snapshot: {bid_count} bids, {ask_count} asks")

        return {
            "bids": [str(o[2]) for o in order_book.bids if not o[2].is_cancelled],
            "asks": [str(o[2]) for o in order_book.asks if not o[2].is_cancelled]
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Zenith Order Matching Engine...")
    logger.info("📍 Server running at http://127.0.0.1:8000")
    logger.info("📚 API documentation at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
