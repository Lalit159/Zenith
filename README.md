

# Zenith: High-Performance Order Matching Engine

Zenith is a lightweight, high-performance order matching engine built in Python. It is designed to simulate a financial exchange by matching buy and sell orders in real-time using optimized data structures.

## 🚀 Features

* **Efficient Matching:** Uses Min/Max Heaps for O(log N) order insertion and O(1) best-price lookup.
* **Fast Cancellations:** Implements a "Lazy Removal" strategy for O(1) order cancellations.
* **RESTful API:** Wrapped in FastAPI for high-concurrency and easy integration.
* **Memory Efficient:** Automatic cleanup of "zombie" (cancelled) orders to prevent memory leaks.

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

uvicorn main:app --reload

The API will be available at:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

Interactive documentation (Swagger UI):
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 📈 API Endpoints

| Method | Endpoint    | Description                      |
| ------ | ----------- | -------------------------------- |
| POST   | /order      | Place a new Buy or Sell order    |
| DELETE | /order/{id} | Cancel an existing order by ID   |
| GET    | /book       | View the current live Order Book |

