import asyncio
import heapq
import json
import logging
import os
import time
from models import Order
from logger import setup_logger

logger = setup_logger(__name__)


class OrderBook:
    def __init__(self):
        self.bids = []  # Max heap (negative price)
        self.asks = []  # Min heap
        self.orders_map = {}  # Track orders by ID
        self.lock = asyncio.Lock()  # The Lock acts as the guard for the entire OrderBook state
        self.log_file = "data/journal.log" # Log file for write-ahead logging (WAL)

    async def add_order(self, order: Order):
        async with self.lock:

            # Write-ahead logging (WAL)
            try:
                with open(self.log_file, "a") as f:

                    log_entry = {
                        "action": "ADD",
                        "id": order.order_id,
                        "side": order.side,
                        "price": order.price,
                        "qty": order.quantity,
                        "ts": order.timestamp
                    }

                    f.write(json.dumps(log_entry) + "\n")
            except IOError as e:
                logger.error(f"Failed to write ADD event to journal.log: {e}")
                raise

            self._internal_add(order)


    async def cancel_order(self, order_id: int):
        async with self.lock:
            if order_id in self.orders_map:
                order = self.orders_map[order_id]
                order.is_cancelled = True

                # 2. Log to Disk (Persistence)
                try:
                    with open(self.log_file, "a") as f:
                        log_entry = {
                        "action": "CANCEL",
                        "id": order_id,
                        "ts": time.time()
                        }
                        f.write(json.dumps(log_entry) + "\n")
                except IOError as e:
                    logger.error(f"Failed to write CANCEL event to journal.log: {e}")

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



    async def load_from_log(self):
        if not os.path.exists(self.log_file):
            return

        logger.info("Rebuilding state from journal.log...")
        async with self.lock:
            with open(self.log_file, "r") as f:
                for line in f:
                    data = json.loads(line)

                    if data["action"] == "ADD":
                        # Check for duplicate order IDs to ensure idempotent recovery
                        if data["id"] in self.orders_map:
                            logger.warning(f"Duplicate order ID {data['id']} found in log, skipping")
                            continue
                        new_order = Order(data["id"], data["side"], data["price"], data["qty"])
                        new_order.timestamp = data["ts"]
                        # Use a simple internal add that doesn't trigger a new log entry
                        self._internal_add(new_order)

                    elif data["action"] == "CANCEL":
                        if data["id"] in self.orders_map:
                            self.orders_map[data["id"]].is_cancelled = True

        logger.info("State recovered successfully.")

    def _internal_add(self, order: Order):
        self.orders_map[order.order_id] = order

        if order.side == 'buy':
            heapq.heappush(self.bids, (-order.price, order.timestamp, order))
            logger.debug(f"Added BUY order to bids heap: {order}")
        else:
            heapq.heappush(self.asks, (order.price, order.timestamp, order))
            logger.debug(f"Added SELL order to asks heap: {order}")

        matches = self.match()
        if matches:
            logger.info(f"Matched {matches} trade(s) for order {order.order_id}")
