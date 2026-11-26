import logging
from types import SimpleNamespace

import pytest

from app.embed import embed_texts


class FakeEmbeddings:
    """Stands in for `client.embeddings`; records calls instead of hitting the API."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, input: list[str], model: str) -> SimpleNamespace:
        self.calls.append({"input": input, "model": model})
        # One fake 3-dim vector per text; first value encodes the position,
        # so tests can check that output order matches input order.
        data = [
            SimpleNamespace(embedding=[float(position), 0.0, 0.0])
            for position in range(len(input))
        ]
        usage = SimpleNamespace(total_tokens=42)
        return SimpleNamespace(data=data, usage=usage)


@pytest.fixture
def fake_client() -> SimpleNamespace:
    """A fake OpenAI client exposing only `embeddings.create`."""
    return SimpleNamespace(embeddings=FakeEmbeddings())


def test_embed_texts_returns_one_vector_per_text_in_order(fake_client):
    vectors = embed_texts(["first", "second", "third"], client=fake_client)

    assert len(vectors) == 3
    assert [vector[0] for vector in vectors] == [0.0, 1.0, 2.0]


def test_embed_texts_sends_all_texts_in_one_call(fake_client):
    embed_texts(["first", "second"], client=fake_client)

    assert len(fake_client.embeddings.calls) == 1
    assert fake_client.embeddings.calls[0]["input"] == ["first", "second"]


def test_embed_texts_empty_input_skips_api_call(fake_client):
    vectors = embed_texts([], client=fake_client)

    assert vectors == []
    assert fake_client.embeddings.calls == []


def test_embed_texts_logs_token_usage(fake_client, caplog):
    with caplog.at_level(logging.INFO, logger="app.embed"):
        embed_texts(["first", "second"], client=fake_client)

    assert "Embedded 2 texts: 42 tokens" in caplog.text
