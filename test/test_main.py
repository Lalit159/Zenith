import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app, order_book



client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_order_book():
    """
    Pytest fixture that clears the order book after each test.

    WHY: We use a shared global order_book singleton (not ideal for testing,
    but requires refactoring main.py to fix). This fixture ensures test isolation
    by cleaning up after each test.

    autouse=True means this fixture automatically runs for every test without
    needing to explicitly request it as a parameter.

    How it works:
    - Code BEFORE yield runs before test (setup phase)
    - yield pauses and lets the test run
    - Code AFTER yield runs after test (teardown/cleanup phase)

    By clearing after each test, we ensure the next test starts with a fresh,
    empty order book state. However, this is NOT true test isolation because:
    - Tests still share the same OrderBook instance
    - If a test fails before cleanup, state can be corrupted
    - Test order can affect results (not idiomatic)

    BETTER SOLUTION: Refactor main.py to use FastAPI dependency injection
    so each test gets its own isolated OrderBook instance. This would be the
    proper way to do real unit testing.
    """
    # Setup phase (before test): Nothing to do, order book starts fresh

    yield  # Test runs here

    # Teardown phase (after test): Clean up for next test
    order_book.bids.clear()      # Clear buy orders heap
    order_book.asks.clear()      # Clear sell orders heap
    order_book.orders_map.clear() # Clear order ID tracking map


# 1. Test the health of the book
def test_read_book():
    """Verify the /book endpoint returns a valid order book structure"""
    response = client.get("/book")
    assert response.status_code == 200
    assert "bids" in response.json()

# 2. Test adding a single limit order
def test_add_order():
    order_data = {
        "order_id": 999,
        "side": "buy",
        "price": 100,
        "quantity": 10
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 200
    assert "Order added successfully" in response.json()["message"]

# 3. Test the Matching Logic (The most important test!)
def test_order_matching():
    # Clear state or use unique IDs for this test
    buy_order = {"order_id": 1001, "side": "buy", "price": 50, "quantity": 5}
    sell_order = {"order_id": 1002, "side": "sell", "price": 50, "quantity": 5}

    # Place Buy
    client.post("/orders", json=buy_order)
    # Place Sell (This should trigger a match)
    response = client.post("/orders", json=sell_order)

    assert response.status_code == 200
    # Check if the response confirms order was added
    assert "Order added successfully" in response.json()["message"]


# 4. Test cancelling an order
def test_cancel_order():
    # First add an order
    order_data = {
        "order_id": 2001,
        "side": "buy",
        "price": 75,
        "quantity": 8
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 200

    # Now cancel it
    response = client.delete("/orders/2001")
    assert response.status_code == 200
    assert "cancelled successfully" in response.json()["message"].lower()


# 5. Test duplicate order ID
def test_duplicate_order_id():
    order_data = {
        "order_id": 5001,
        "side": "buy",
        "price": 100,
        "quantity": 5
    }

    # First order should succeed
    response1 = client.post("/orders", json=order_data)
    assert response1.status_code == 200

    # Duplicate should fail with 400 Bad Request
    response2 = client.post("/orders", json=order_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


# 6. Test invalid order data - invalid side
def test_invalid_order_side():
    order_data = {
        "order_id": 5002,
        "side": "invalid",
        "price": 100,
        "quantity": 5
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 422  # Pydantic validation error

# 7. Test invalid order data - negative price
def test_invalid_order_price():
    order_data = {
        "order_id": 5003,
        "side": "buy",
        "price": -100,
        "quantity": 5
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 422  # Pydantic validation error

# 8. Test invalid order data - zero quantity
def test_invalid_order_quantity():
    order_data = {
        "order_id": 5004,
        "side": "buy",
        "price": 100,
        "quantity": 0
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 422  # Pydantic validation error

# 9. Test cancel non-existent order
def test_cancel_nonexistent_order():
    response = client.delete("/orders/9999")
    assert response.status_code == 404

# 10. Test order book structure
def test_order_book_structure():
    """Verify the order book response contains all required fields with correct types"""
    response = client.get("/book")
    assert response.status_code == 200
    data = response.json()

    # Check for required keys
    assert "bids" in data
    assert "asks" in data
    assert "bid_count" in data
    assert "ask_count" in data

    # Check types
    assert isinstance(data["bids"], list)
    assert isinstance(data["asks"], list)
    assert isinstance(data["bid_count"], int)
    assert isinstance(data["ask_count"], int)
