# Creating Zenith - Real-time order matching engine

import time
import heapq

class Order:
    def __init__(self, order_id, side, price, quantity):
        self.order_id = order_id
        self.side = side.lower()  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity
        self.timestamp = time.time()

    def __repr__(self): # For debugging purposes for developers
        return f"Order(id={self.order_id}, side={self.side.upper()}, price={self.price}, quantity={self.quantity})"

    def __str__(self):
        return f"Order id={self.order_id}, side={self.side.upper()}, price={self.price}, quantity={self.quantity})"


class OrderBook:
    def __init__(self):
        self.buys = [] # Min heap(negative price for max-heap behavior)
        self.asks = [] # Min heap (standard)

    def add_order(self, order):
        if order.side == 'buy':
            # Storing -100 makes it "smaller" than -90, so it stays at the top.
            heapq.heappush(self.buys, (-order.price, order.timestamp, order))
        else:
            heapq.heappush(self.asks, (order.price, order.timestamp, order))

        self.match() # After adding, try to match orders

    def match(self):
        while self.buys and self.asks:
            best_bid = self.buys[0]
            best_ask = self.asks[0]

            if best_bid.price >= best_ask.price: # If there's a match
                trade_price = best_ask.price
                trade_quantity = min(best_bid.quantity, best_ask.quantity)

                print(f"Trade executed: {trade_quantity} @ {trade_price}")

                best_bid.quantity -= trade_quantity
                best_ask.quantity -= trade_quantity

                if best_bid.quantity == 0:
                    self.buys.pop(0) # Remove fully filled buy order
                if best_ask.quantity == 0:
                    self.asks.pop(0) # Remove fully filled sell order

            else:
                print("No match found, stopping matching process.")
                break # No more matches possible


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

if __name__ == "__main__":
    main()

