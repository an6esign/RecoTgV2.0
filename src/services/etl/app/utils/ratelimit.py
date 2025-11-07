import asyncio, random, time

class TokenBucket:
    def __init__(self, rate_per_sec: float, burst: int = 1):
        self.rate = rate_per_sec
        self.capacity = burst
        self.tokens = burst
        self.updated = time.monotonic()
        self._lock = asyncio.Lock()

    async def wait(self):
        async with self._lock:
            now = time.monotonic()
            delta = now - self.updated
            self.updated = now
            self.tokens = min(self.capacity, self.tokens + delta * self.rate)
            if self.tokens < 1:
                need = (1 - self.tokens) / self.rate
                await asyncio.sleep(need)
                self.tokens = 0
            else:
                self.tokens -= 1

async def human_sleep(min_ms=300, max_ms=900):
    await asyncio.sleep(random.uniform(min_ms/1000, max_ms/1000))
