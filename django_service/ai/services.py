import logging
from math import sqrt

from django.conf import settings
from tenacity import retry, stop_after_attempt, wait_fixed

from .models import AIRequestLog, TaskEmbedding
from .providers import DummyProvider

logger = logging.getLogger(__name__)

BANNED_TERMS = {"hack", "exploit malware", "kill"}


class ModerationError(ValueError):
    pass


def assert_safe_prompt(text: str):
    if len(text) > 5000:
        raise ModerationError("Input too long")
    lower = text.lower()
    if any(term in lower for term in BANNED_TERMS):
        raise ModerationError("Input blocked by moderation policy")


def provider():
    return DummyProvider()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
def summarize(user, text: str):
    assert_safe_prompt(text)
    result = provider().summarize(text)
    AIRequestLog.objects.create(user=user, feature="summarize", prompt=text, response={"summary": result})
    return result


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
def prioritize(user, title: str, description: str):
    assert_safe_prompt(f"{title} {description}")
    score = provider().prioritize(title, description)
    AIRequestLog.objects.create(user=user, feature="prioritize", prompt=title, response={"score": score})
    return score


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
def parse_task(user, text: str):
    assert_safe_prompt(text)
    data = provider().parse_task(text)
    AIRequestLog.objects.create(user=user, feature="parse", prompt=text, response=data)
    return data


def upsert_embedding(task):
    raw = f"{task.title}\n{task.description}"
    vector = provider().embed(raw)
    TaskEmbedding.objects.update_or_create(task=task, defaults={"vector": vector, "source_text": raw})


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)
