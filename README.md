

# Zenith: High-Performance Order Matching Engine

Zenith is a lightweight, high-performance order matching engine built in Python. It is designed to simulate a financial exchange by matching buy and sell orders in real-time using optimized data structures.

## 🚀 Features

* **Efficient Matching:** Uses Min/Max Heaps for O(log N) order insertion and O(1) best-price lookup.
* **Fast Cancellations:** Implements a "Lazy Removal" strategy for O(1) order cancellations.
* **RESTful API:** Wrapped in FastAPI for high-concurrency and easy integration.
* **Memory Efficient:** Automatic cleanup of "zombie" (cancelled) orders to prevent memory leaks.
* **Persistence & Recovery:** Write-Ahead Logging (WAL) ensures no order data is lost on crashes; automatic state recovery on startup.

## 🏗️ Architecture

The engine maintains two Priority Queues:

* **Bids (Buy Orders):** A Max-Heap prioritizing the highest price.
* **Asks (Sell Orders):** A Min-Heap prioritizing the lowest price.

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **Framework:** FastAPI
* **Concurrency:** Asyncio / Uvicorn
* **Data Structures:** heapq (Priority Queues), dict (Hash Maps for O(1) lookups)

## 🚦 Getting Started

### Prerequisites

* Python 3.11 or higher
* pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Lalit159/Zenith.git
   cd zenith
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

Interactive documentation (Swagger UI):
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 📈 API Endpoints

| Method | Endpoint        | Description                      |
| ------ | --------------- | -------------------------------- |
| POST   | /orders         | Place a new Buy or Sell order    |
| DELETE | /orders/{id}    | Cancel an existing order by ID   |
| GET    | /book           | View the current live Order Book |

## 🐳 Docker

Build and run the application in a Docker container:

```sh
docker build -t zenith-engine .
docker run -p 8000:8000 zenith-engine
```

**Note:** Persistence (WAL logs) is not yet working in Docker environments. For production persistence, run locally or implement volume mounting properly.

## 📦 Project Structure

```
Zenith/
├── main.py                      # FastAPI entry point
├── order_book.py                # Core order matching engine
├── models.py                    # Order and Trade data models
├── logger.py                    # Centralized logging configuration
├── config.py                    # Constants & configuration
├── test_order_concurrency.py    # Stress test (throughput benchmarking)
├── Dockerfile                   # Docker container definition
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── LOGGING.md                   # Logging documentation
├── Technical_Challenges.md      # Known issues & solutions
├── data/                        # Persistent data (git-ignored)
│   └── journal.log              # Write-Ahead Log for recovery
├── logs/                        # Application logs (git-ignored)
│   ├── main.log
│   ├── order_book.log
│   └── test_order_concurrency.log
└── .dockerignore                # Docker build exclusions
```

### Key Files

- **`order_book.py`** - OrderBook class with matching logic, heap management, and WAL
- **`logger.py`** - Dual output logging (console: INFO, files: DEBUG) with log rotation
- **`main.py`** - FastAPI REST API for placing/cancelling orders and viewing the book
- **`models.py`** - Order dataclass with idempotency and timestamp tracking

---

