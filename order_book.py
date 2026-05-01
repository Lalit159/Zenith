import asyncio
import heapq
import logging
from models import Order
from logger import setup_logger

logger = setup_logger(__name__)


class OrderBook:
    def __init__(self):
        self.bids = []  # Max heap (negative price)
        self.asks = []  # Min heap
        self.orders_map = {}  # Track orders by ID
        self.lock = asyncio.Lock()  # The Lock acts as the guard for the entire OrderBook state

    async def add_order(self, order: Order):
        async with self.lock:
            self.orders_map[order.order_id] = order
            logger.debug(f"Order added to map: {order}")

            if order.side == 'buy':
                heapq.heappush(self.bids, (-order.price, order.timestamp, order))
                logger.debug(f"BUY order pushed to bids heap: {order}")
            else:
                heapq.heappush(self.asks, (order.price, order.timestamp, order))
                logger.debug(f"SELL order pushed to asks heap: {order}")

            matches = self.match()
            if matches:
                logger.info(f"Matched {matches} trade(s) for order {order.order_id}")

    async def cancel_order(self, order_id: int):
        async with self.lock:
            if order_id in self.orders_map:
                order = self.orders_map[order_id]
                order.is_cancelled = True
                logger.info(f"Order {order_id} marked as cancelled: {order}")
            else:
                logger.warning(f"Attempted to cancel non-existent order {order_id}")

    def _remove_order(self, heap, order_id: int):
        heapq.heappop(heap)
        self.orders_map.pop(order_id, None)
        logger.debug(f"Removed order {order_id} from heap and map")

    def match(self):
        matches_count = 0
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
                matches_count += 1

                logger.info(
                    f"🔗 TRADE EXECUTED | Qty: {trade_quantity} | Price: ${trade_price} | "
                    f"BuyOrder: {best_bid.order_id} | SellOrder: {best_ask.order_id}"
                )

                best_bid.quantity -= trade_quantity
                best_ask.quantity -= trade_quantity

                if best_bid.quantity == 0:
                    self._remove_order(self.bids, best_bid.order_id)

                if best_ask.quantity == 0:
                    self._remove_order(self.asks, best_ask.order_id)
            else:
                logger.debug(
                    f"No match found | Best Bid: ${best_bid_price} | Best Ask: ${best_ask_price}"
                )
                break

        return matches_count
