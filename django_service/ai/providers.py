import hashlib
import random


class BaseProvider:
    def summarize(self, text: str) -> str:
        raise NotImplementedError

    def prioritize(self, title: str, description: str) -> float:
        raise NotImplementedError

    def parse_task(self, text: str) -> dict:
        raise NotImplementedError

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class DummyProvider(BaseProvider):
    def summarize(self, text: str) -> str:
        words = text.strip().split()
        return " ".join(words[:25]) if words else "No content"

    def prioritize(self, title: str, description: str) -> float:
        urgency_terms = ["urgent", "asap", "today", "blocker", "critical"]
        content = f"{title} {description}".lower()
        matches = sum(1 for term in urgency_terms if term in content)
        return min(100.0, 20.0 + matches * 15.0 + len(description) / 20)

    def parse_task(self, text: str) -> dict:
        title = text.split(".")[0][:80] or "Generated task"
        return {"title": title.strip(), "description": text.strip(), "status": "todo"}

    def embed(self, text: str) -> list[float]:
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)
        rng = random.Random(seed)
        return [round(rng.random(), 6) for _ in range(16)]
