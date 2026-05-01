# Creating Zenith - Real-time order matching engine

from fastapi import FastAPI, HTTPException
from models import Order, OrderRequest
from order_book import OrderBook


# NOTE: FastAPI concurrency model:
# - def → runs in threadpool (blocking, separate thread)
# - async def → runs in event loop (non-blocking, single thread via await)
# - Our OrderBook is CPU-bound (in-memory), so no I/O bottleneck.
# - If adding database/API calls, use async/await to avoid blocking event loop.

app = FastAPI()
order_book = OrderBook()

@app.get("/")
async def root():
    return {"message": "Welcome to Zenith - Real-time Order Matching Engine!"}


@app.post("/orders")
async def create_order(order_request: OrderRequest):
    if order_request.order_id in order_book.orders_map:
        raise HTTPException(status_code=400, detail="Order ID already exists.")

    order = Order(order_request.order_id, order_request.side, order_request.price, order_request.quantity)
    await order_book.add_order(order)
    return {"message": "Order added successfully."}


@app.delete("/orders/{order_id}")
async def cancel_order(order_id: int):
    if order_id not in order_book.orders_map:
        raise HTTPException(status_code=404, detail="Order ID not found.")

    await order_book.cancel_order(order_id)
    return {"message": "Order cancelled successfully."}


@app.get("/book")
async def get_order_book():
    async with order_book.lock:
        return {
            "bids": [str(o[2]) for o in order_book.bids if not o[2].is_cancelled],
            "asks": [str(o[2]) for o in order_book.asks if not o[2].is_cancelled]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
