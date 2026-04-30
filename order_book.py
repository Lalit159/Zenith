import heapq
from models import Order


class OrderBook:
    def __init__(self):
        self.bids = []  # Max heap (negative price)
        self.asks = []  # Min heap
        self.orders_map = {}  # Track orders by ID

    def add_order(self, order: Order):
        self.orders_map[order.order_id] = order

        if order.side == 'buy':
            heapq.heappush(self.bids, (-order.price, order.timestamp, order))
        else:
            heapq.heappush(self.asks, (order.price, order.timestamp, order))

        self.match()

    def cancel_order(self, order_id: int):
        if order_id in self.orders_map:
            order = self.orders_map[order_id]
            order.is_cancelled = True
            print(f"Order {order_id} cancelled.")
        else:
            print(f"Order {order_id} not found for cancellation.")

    def _remove_order(self, heap, order_id: int):
        heapq.heappop(heap)
        self.orders_map.pop(order_id, None)

    def match(self):
        while self.bids and self.asks:
            best_bid_neg_price, bid_time, best_bid = self.bids[0]
            best_ask_price, ask_time, best_ask = self.asks[0]

            if best_bid.is_cancelled:
                self._remove_order(self.bids, best_bid.order_id)
                continue

            if best_ask.is_cancelled:
                self._remove_order(self.asks, best_ask.order_id)
                continue

            best_bid_price = -best_bid_neg_price

            if best_bid_price >= best_ask_price:
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
                break
