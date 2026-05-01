import time
from pydantic import BaseModel, field_validator, Field


class Order:
    def __init__(self, order_id, side, price, quantity):
        # Validate inputs
        if not isinstance(order_id, int) or order_id <= 0:
            raise ValueError(f"Order ID must be a positive integer, got: {order_id}")
        
        side_lower = side.lower()
        if side_lower not in ('buy', 'sell'):
            raise ValueError(f"Side must be 'buy' or 'sell', got: {side}")
        
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError(f"Price must be a positive number, got: {price}")
        
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError(f"Quantity must be a positive number, got: {quantity}")
        
        self.order_id = order_id
        self.side = side_lower
        self.price = float(price)
        self.quantity = float(quantity)
        self.timestamp = time.time()
        self.is_cancelled = False

    def __repr__(self):
        return f"Order(id={self.order_id}, side={self.side.upper()}, price={self.price}, quantity={self.quantity})"

    def __str__(self):
        return f"Order(id={self.order_id}, side={self.side.upper()}, price={self.price}, quantity={self.quantity})"


class OrderRequest(BaseModel):
    order_id: int = Field(..., gt=0, description="Positive integer order ID")
    side: str = Field(..., description="Order side: 'buy' or 'sell'")
    price: float = Field(..., gt=0, description="Positive price per unit")
    quantity: int = Field(..., gt=0, description="Positive order quantity")

    @field_validator('side')
    @classmethod
    def validate_side(cls, v):
        if v.lower() not in ('buy', 'sell'):
            raise ValueError("Side must be 'buy' or 'sell'")
        return v.lower()
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v
