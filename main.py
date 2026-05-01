# Creating Zenith - Real-time order matching engine

import logging
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models import Order, OrderRequest
from order_book import OrderBook
from logger import setup_logger
from config import SERVER_HOST, SERVER_PORT, get_config_summary
from contextlib import asynccontextmanager

logger = setup_logger(__name__)
order_book = OrderBook()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs ON STARTUP
    await order_book.load_from_log()
    yield

    # This runs ON SHUTDOWN
    print("Shutting down engine...")



# NOTE: FastAPI concurrency model:
# - def → runs in threadpool (blocking, separate thread)
# - async def → runs in event loop (non-blocking, single thread via await)
# - Our OrderBook is CPU-bound (in-memory), so no I/O bottleneck.
# - If adding database/API calls, use async/await to avoid blocking event loop.

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    logger.debug("GET / - Root endpoint accessed")
    return {"message": "Welcome to Zenith - Real-time Order Matching Engine!"}


@app.post("/orders")
async def create_order(order_request: OrderRequest):
    logger.debug(f"POST /orders - Received order request: {order_request}")

    try:
        # Check for duplicate order ID
        if order_request.order_id in order_book.orders_map:
            logger.error(f"Order ID {order_request.order_id} already exists")
            raise HTTPException(
                status_code=400,
                detail=f"Order ID {order_request.order_id} already exists."
            )

        # Create order (will validate all fields)
        order = Order(
            order_request.order_id,
            order_request.side,
            order_request.price,
            order_request.quantity
        )
        logger.info(f"✅ Creating new order: {order}")

        await order_book.add_order(order)
        return {
            "message": "Order added successfully.",
            "order_id": order.order_id,
            "side": order.side,
            "price": order.price,
            "quantity": order.quantity
        }

    except ValueError as e:
        logger.error(f"Invalid order data: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid order data: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create order.")


@app.delete("/orders/{order_id}")
async def cancel_order(order_id: int):
    logger.debug(f"DELETE /orders/{order_id} - Received cancellation request")

    try:
        # Validate order_id
        if not isinstance(order_id, int) or order_id <= 0:
            logger.error(f"Invalid order ID: {order_id}")
            raise HTTPException(
                status_code=400,
                detail="Order ID must be a positive integer."
            )

        if order_id not in order_book.orders_map:
            logger.error(f"Attempted to cancel non-existent order {order_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Order ID {order_id} not found."
            )

        # Check if already cancelled
        if order_book.orders_map[order_id].is_cancelled:
            logger.warning(f"Order {order_id} is already cancelled")
            raise HTTPException(
                status_code=400,
                detail=f"Order ID {order_id} is already cancelled."
            )

        logger.info(f"🗑️  Cancelling order {order_id}")
        await order_book.cancel_order(order_id)
        return {
            "message": "Order cancelled successfully.",
            "order_id": order_id
        }

    except HTTPException:
        raise # This re-raises the HTTPException that was just caught
    except Exception as e:
        logger.error(f"Unexpected error cancelling order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel order.")


@app.get("/book")
async def get_order_book():
    logger.debug("GET /book - Retrieving order book snapshot")

    try:
        async with order_book.lock:
            bid_count = len([o for o in order_book.bids if not o[2].is_cancelled])
            ask_count = len([o for o in order_book.asks if not o[2].is_cancelled])
            logger.debug(f"Order book snapshot: {bid_count} bids, {ask_count} asks")

            return {
                "bids": [str(o[2]) for o in order_book.bids if not o[2].is_cancelled],
                "asks": [str(o[2]) for o in order_book.asks if not o[2].is_cancelled],
                "bid_count": bid_count,
                "ask_count": ask_count
            }
    except Exception as e:
        logger.error(f"Error retrieving order book: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve order book.")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Zenith Order Matching Engine...")

    # Log configuration summary
    config_summary = get_config_summary()
    for key, value in config_summary.items():
        logger.info(f"   {key}: {value}")

    logger.info(f"📍 Server running at http://{SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"📚 API documentation at http://{SERVER_HOST}:{SERVER_PORT}/docs")
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
