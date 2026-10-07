"""Trimmed tool results must stay valid JSON: clients parse them (OmniOP builds cards from them)."""

import json

from app.services.dispatcher import MAX_LIST_CHARS, _trim


def test_small_result_is_unchanged() -> None:
    data = {"bots": [{"id": 1, "name": "A"}], "total_records": 1}
    assert json.loads(_trim(data).text) == data


def test_long_list_is_cut_to_whole_items_with_the_note_inside_the_json() -> None:
    data = {"bots": [{"id": i, "prompt": "x" * 500} for i in range(200)], "total_records": 200}
    text = _trim(data).text
    assert len(text) <= MAX_LIST_CHARS + 500
    parsed = json.loads(text)
    assert 1 <= len(parsed["bots"]) < 200
    assert all(set(b) == {"id", "prompt"} for b in parsed["bots"])
    assert "Showing" in parsed["_note"] and "of 200" in parsed["_note"]
    assert parsed["total_records"] == 200


def test_one_oversized_item_keeps_its_shape_and_shortens_long_text() -> None:
    call = {"id": 173415, "bot_name": "Test Call Agent", "call_conversation": "y" * 61_000}
    text = _trim({"call_log_data": [call], "total_records": 1}).text
    assert len(text) <= MAX_LIST_CHARS + 500
    parsed = json.loads(text)
    (kept,) = parsed["call_log_data"]
    assert kept["id"] == 173415 and kept["bot_name"] == "Test Call Agent"
    assert len(kept["call_conversation"]) < 61_000
    assert "truncated" in kept["call_conversation"]
    assert "truncated" in parsed["_note"]


def test_oversized_object_without_a_list_stays_valid_json() -> None:
    data = {"id": 9, "prompt": "z" * 80_000}
    parsed = json.loads(_trim(data).text)
    assert parsed["id"] == 9 and len(parsed["prompt"]) < 80_000
