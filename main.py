# Creating Zenith - Real-time order matching engine

import time
import heapq


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

class Order:
    def __init__(self, order_id, side, price, quantity):
        self.order_id = order_id
        self.side = side.lower()  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity
        self.timestamp = time.time()
        self.is_cancelled = False  # To handle order cancellations in the future

    def __repr__(self): # For debugging purposes for developers
        return f"Order(id={self.order_id}, side={self.side.upper()}, price={self.price}, quantity={self.quantity})"

    def __str__(self):
        return f"Order id={self.order_id}, side={self.side.upper()}, price={self.price}, quantity={self.quantity})"


class OrderBook:
    def __init__(self):
        self.bids = [] # Min heap(negative price for max-heap behavior)
        self.asks = [] # Min heap (standard)
        self.orders_map = {} # To keep track of orders by ID for potential cancellations

    def add_order(self, order):
        self.orders_map[order.order_id] = order # Store order in map for easy access

        if order.side == 'buy':
            # Storing -100 makes it "smaller" than -90, so it stays at the top.
            heapq.heappush(self.bids, (-order.price, order.timestamp, order))
        else:
            heapq.heappush(self.asks, (order.price, order.timestamp, order))

        self.match() # After adding, try to match orders

    def cancel_order(self, order_id):
        if order_id in self.orders_map:
            order = self.orders_map[order_id]
            order.is_cancelled = True
            print(f"Order {order_id} cancelled.")
        else:
            print(f"Order {order_id} not found for cancellation.")

    def _remove_order(self, heap, order_id):
        if heap == self.bids:
            heapq.heappop(self.bids)
        else:
            heapq.heappop(self.asks)
        self.orders_map.pop(order_id, None)

    def match(self):
        while self.bids and self.asks:
            # peek at the top of both heaps
            best_bid_neg_price, bid_time, best_bid = self.bids[0]
            best_ask_price, ask_time, best_ask = self.asks[0]

            if best_bid.is_cancelled:
                self._remove_order(self.bids, best_bid.order_id)
                continue

            if best_ask.is_cancelled:
                self._remove_order(self.asks, best_ask.order_id)
                continue

            # Convert back to positive for the comparison
            best_bid_price = -best_bid_neg_price


            if best_bid_price >= best_ask_price: # If there's a match
                trade_price = best_ask.price
                trade_quantity = min(best_bid.quantity, best_ask.quantity)

                print(f"Trade executed: {trade_quantity} @ {trade_price}")

                best_bid.quantity -= trade_quantity
                best_ask.quantity -= trade_quantity

                if best_bid.quantity == 0:
                    self._remove_order(self.bids, best_bid.order_id)

                if best_ask.quantity == 0:
                    self._remove_order(self.asks, best_ask.order_id)

            else:
                print("No match found, stopping matching process.")
                break # No more matches possible


class OrderRequest(BaseModel):
    order_id: int
    side: str
    price: float
    quantity: int

app = FastAPI()
order_book = OrderBook()

@app.post("/orders")
def create_order(order_request: OrderRequest):
    order_id = order_request.order_id
    if order_id in order_book.orders_map:
        raise HTTPException(status_code=400, detail="Order ID already exists.")

    order = Order(order_id, order_request.side, order_request.price, order_request.quantity)
    order_book.add_order(order)
    return {"message": "Order added successfully."}


@app.delete("/orders/{order_id}")
def cancel_order(order_id: int):
    if order_id not in order_book.orders_map:
        raise HTTPException(status_code=404, detail="Order ID not found.")

    order_book.cancel_order(order_id)
    return {"message": "Order cancelled successfully."}

@app.get("/book")
def get_order_book():
    return {
        "bids": [str(o[2]) for o in order_book.bids if not o[2].is_cancelled],
        "asks": [str(o[2]) for o in order_book.asks if not o[2].is_cancelled]
    }


def main():
    order_book = OrderBook()

    # Sample orders for testing
    orders = [
        Order(1, 'buy', 100, 10),
        Order(2, 'sell', 99, 5),
        Order(3, 'sell', 101, 10),
        Order(4, 'buy', 102, 15),
        Order(5, 'sell', 101, 5),
        Order(6, 'sell', 102, 10)
    ]

    for order in orders:
        print(f"Adding {order}")
        order_book.add_order(order)

    # Sample cancellation
    order_book.cancel_order(3)
    order_book.cancel_order(6)

# if __name__ == "__main__":
#     main()



