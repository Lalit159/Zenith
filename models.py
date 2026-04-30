import time
from pydantic import BaseModel


class Order:
    def __init__(self, order_id, side, price, quantity):
        self.order_id = order_id
        self.side = side.lower()  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity
        self.timestamp = time.time()
        self.is_cancelled = False

    def __repr__(self):
        return f"Order(id={self.order_id}, side={self.side.upper()}, price={self.price}, quantity={self.quantity})"

    def __str__(self):
        return f"Order(id={self.order_id}, side={self.side.upper()}, price={self.price}, quantity={self.quantity})"


class OrderRequest(BaseModel):
    order_id: int
    side: str
    price: float
    quantity: int
