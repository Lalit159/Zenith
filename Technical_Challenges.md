# Technical Challenges & Design Decisions

### 1. Challenge: Algorithmic Efficiency in High-Volume Environments
**Problem:** In early versions, sorting the order book after every new order resulted in $O(N \log N)$ time complexity. In a high-frequency trading environment, this latency is unacceptable.
**Solution:** I refactored the engine to use **Priority Queues (Heaps)**.
- **Impact:** Order insertion was reduced to $O(\log N)$ and finding the "Best Bid/Ask" became an $O(1)$ operation. This allows the system to scale to thousands of orders without a linear drop in performance.

### 2. Challenge: Efficient Cancellations in a Heap
**Problem:** Heaps are not designed for searching or removing specific elements from the middle of the tree ($O(N)$ search time).
**Solution:** I implemented a **Lazy Removal** pattern combined with a **Hash Map** (`orders_map`).
- **Mechanism:** Instead of physically removing a cancelled order from the heap, I mark it as `is_cancelled = True` in the map ($O(1)$). The matching engine then ignores these "zombie" orders when they eventually float to the top of the heap.
- **Trade-off:** I traded a small amount of memory (storing the cancelled flag) for significantly lower latency on the cancellation path.

### 3. Challenge: Memory Management & "Zombie" Cleanup
**Problem:** Lazy removal can lead to memory leaks if cancelled orders remain in the heap/map indefinitely.
**Solution:** I integrated a housekeeping step within the `match()` function.
- **Mechanism:** Before every match, the engine checks the top of both heaps. If the top order is marked as cancelled, it is "popped" and removed from the map. This ensures that the memory footprint stays proportional to the number of *active* orders rather than the total history of orders.

### 4. Future Roadmap: Thread Safety & Persistence
**Current Limitation:** The current version is in-memory and not thread-safe for high-concurrency writes.
**Next Steps:**
- **Concurrency:** I plan to implement a **Read-Write Lock** or use a **Single-Threaded Event Loop** (similar to Node.js or Redis) to ensure the order book remains consistent when multiple users trade simultaneously.
- **Persistence:** To handle system crashes, I intend to implement a **Write-Ahead Log (WAL)** to record every order to disk before it's processed, allowing for full state recovery.
