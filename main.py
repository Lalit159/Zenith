# Creating Zenith - Real-time order matching engine

import time

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
        self.buys = [] # List of buy orders
        self.asks = [] # List of sell orders

    def add_order(self, order):
        if order.side == 'buy':
            self.buys.append(order)
            self.buys.sort(key = lambda x: x.price, reverse=True) # Sort buy orders by price descending
        else:
            self.asks.append(order)
            self.asks.sort(key = lambda x: x.price) # Sort sell orders by price ascending

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

