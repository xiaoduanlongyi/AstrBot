import asyncio

import pytest

from astrbot.core.platform.sources.weixin_oc.weixin_oc_adapter import WeixinOCAdapter


@pytest.mark.asyncio
async def test_weixin_oc_splits_long_text_before_send(monkeypatch):
    adapter = WeixinOCAdapter(
        {
            "id": "weixin_oc_test",
            "type": "weixin_oc",
            "weixin_oc_text_item_character_limit": 100,
        },
        {},
        asyncio.Queue(),
    )
    sent_texts = []

    async def fake_send_items(user_id, item_list, **kwargs):  # noqa: ARG001
        sent_texts.append(item_list[0]["text_item"]["text"])
        return True

    monkeypatch.setattr(adapter, "_send_items_to_session", fake_send_items)

    assert await adapter._send_to_session(
        "user-id",
        "first sentence. second sentence. third sentence. fourth sentence. "
        "fifth sentence. sixth sentence. seventh sentence. final sentence.",
    )

    assert len(sent_texts) > 1
    assert all(0 < len(text) <= 100 for text in sent_texts)
    assert " ".join(sent_texts) == (
        "first sentence. second sentence. third sentence. fourth sentence. "
        "fifth sentence. sixth sentence. seventh sentence. final sentence."
    )


@pytest.mark.asyncio
async def test_weixin_oc_keeps_short_text_as_single_message(monkeypatch):
    adapter = WeixinOCAdapter(
        {
            "id": "weixin_oc_test",
            "type": "weixin_oc",
            "weixin_oc_text_item_character_limit": 20,
        },
        {},
        asyncio.Queue(),
    )
    sent_texts = []

    async def fake_send_items(user_id, item_list, **kwargs):  # noqa: ARG001
        sent_texts.append(item_list[0]["text_item"]["text"])
        return True

    monkeypatch.setattr(adapter, "_send_items_to_session", fake_send_items)

    assert await adapter._send_to_session("user-id", "short message")

    assert sent_texts == ["short message"]
