import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


# Mocking SessionMetadata since Pydantic is not available in this environment
@dataclass
class SessionMetadata:
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    emotion_events: List = None
    code_insights: List = None
    was_recovered: bool = False

    def __init__(self, **kwargs):
        self.session_id = kwargs.get("session_id", "unknown")
        self.user_id = kwargs.get("user_id", "unknown")
        self.start_time = kwargs.get("start_time", datetime.utcnow())
        self.end_time = kwargs.get("end_time")
        self.emotion_events = kwargs.get("emotion_events", [])
        self.code_insights = kwargs.get("code_insights", [])
        self.was_recovered = kwargs.get("was_recovered", False)


class MockDoc:
    def __init__(self, id, data):
        self.id = id
        self._data = data

    def to_dict(self):
        return self._data


class MockQuery:
    def __init__(self, docs):
        self.docs = docs

    def stream(self):
        # Simulate network delay for each doc in stream
        for doc in self.docs:
            time.sleep(0.01)  # 10ms delay per doc
            yield doc

    def get(self):
        # Simulate network delay for batch get
        time.sleep(0.05)  # 50ms flat delay for the whole batch
        return self.docs


async def original_fetch(query):
    # This is the current implementation in queries.py
    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        # Parse to Pydantic (simulated here)
        results.append(SessionMetadata(**data))
    return results


async def optimized_fetch(query):
    # This is the proposed implementation
    def _fetch_and_parse():
        docs = query.get()
        return [
            SessionMetadata(**{**doc.to_dict(), "session_id": doc.id}) for doc in docs
        ]

    return await asyncio.to_thread(_fetch_and_parse)


async def main():
    print("Establish Baseline Benchmark for get_recent_sessions")

    # Setup mock data (10 sessions)
    mock_data = [
        {"user_id": "user123", "start_time": datetime.utcnow()} for _ in range(10)
    ]
    docs = [MockDoc(f"doc_{i}", data) for i, data in enumerate(mock_data)]
    query = MockQuery(docs)

    # Warm up
    await original_fetch(query)
    await optimized_fetch(query)

    # Measure original
    start = time.perf_counter()
    for _ in range(5):
        await original_fetch(query)
    original_time = (time.perf_counter() - start) / 5
    print(f"Original average time: {original_time * 1000:.2f}ms")

    # Measure optimized
    start = time.perf_counter()
    for _ in range(5):
        await optimized_fetch(query)
    optimized_time = (time.perf_counter() - start) / 5
    print(f"Optimized average time: {optimized_time * 1000:.2f}ms")

    improvement = (original_time - optimized_time) / original_time * 100
    print(f"Improvement: {improvement:.2f}%")


if __name__ == "__main__":
    asyncio.run(main())
