"""A call log over the size cap still reaches the agent as valid JSON with transcript and cost."""

import json
from typing import Any

from app.services.dispatcher import MAX_LIST_CHARS, _trim


def _call_log(i: int, turns: int = 20) -> dict[str, Any]:
    return {
        "id": i,
        "call_conversation": "user: hello\nbot: hi there\n" * 60,
        "recording_url": f"https://example.com/rec/{i}.mp3",
        "call_cost": 0.42,
        "call_status": "completed",
        "interactions": [
            {"interaction_sequence": t, "user_query": "q" * 300, "bot_response": "r" * 900}
            for t in range(turns)
        ],
    }


def _payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"call_log_data": rows, "total_records": len(rows)}


def _json_part(text: str) -> Any:
    return json.loads(text)


def test_one_large_call_log_keeps_transcript_recording_and_cost() -> None:
    payload = _payload([_call_log(1)])
    assert len(json.dumps(payload, indent=2)) > MAX_LIST_CHARS

    text = _trim(payload).text
    row = _json_part(text)["call_log_data"][0]

    assert len(text) <= MAX_LIST_CHARS + 300
    assert row["call_conversation"] == payload["call_log_data"][0]["call_conversation"]
    assert row["recording_url"] == "https://example.com/rec/1.mp3"
    assert row["call_cost"] == 0.42
    assert "interactions" not in row
    assert "interactions" in _json_part(text)["_note"]


def test_a_page_of_call_logs_drops_turn_detail_before_rows() -> None:
    payload = _payload([_call_log(i) for i in range(10)])

    data = _json_part(_trim(payload).text)

    assert len(data["call_log_data"]) == 10
    assert all("interactions" not in row for row in data["call_log_data"])


def test_a_small_call_log_keeps_its_turn_detail() -> None:
    payload = _payload([_call_log(1, turns=2)])
    assert len(json.dumps(payload, indent=2)) <= MAX_LIST_CHARS

    row = json.loads(_trim(payload).text)["call_log_data"][0]

    assert len(row["interactions"]) == 2


def test_the_note_says_turn_detail_was_dropped_when_rows_go_too() -> None:
    payload = _payload([_call_log(i) for i in range(30)])

    text = _trim(payload).text

    assert len(_json_part(text)["call_log_data"]) < 30
    assert "of 30 items. Left out per-turn detail" in text


def test_a_cut_page_never_hands_back_a_cursor_that_skips_the_cut_rows() -> None:
    rows = [{"id": i, "custom_variables": {"note": "x" * 2000}} for i in range(150)]
    payload = {"records": rows, "has_more": True, "next_cursor": "past-row-150"}
    result = _trim(payload).text
    data = _json_part(result)
    assert len(data["records"]) < 150
    assert "next_cursor" not in data
    assert "has_more" not in data
    assert f"pagesize {len(data['records'])}" in result


def test_a_page_that_fits_keeps_its_cursor() -> None:
    payload = {"records": [{"id": 1}], "has_more": True, "next_cursor": "abc"}
    assert _json_part(_trim(payload).text)["next_cursor"] == "abc"


def test_one_oversized_item_keeps_its_shape_and_shortens_long_text() -> None:
    call = {"id": 173415, "bot_name": "Test Call Agent", "call_conversation": "y" * 61_000}
    text = _trim({"call_log_data": [call], "total_records": 1}).text
    assert len(text) <= MAX_LIST_CHARS
    parsed = json.loads(text)
    (kept,) = parsed["call_log_data"]
    assert kept["id"] == 173415 and kept["bot_name"] == "Test Call Agent"
    assert "truncated" in kept["call_conversation"]
    assert "truncated" in parsed["_note"]


def test_oversized_object_without_a_list_stays_valid_json() -> None:
    parsed = json.loads(_trim({"id": 9, "prompt": "z" * 80_000}).text)
    assert parsed["id"] == 9 and len(parsed["prompt"]) < 80_000


def test_one_item_with_a_long_nested_list_is_shortened_not_dropped() -> None:
    turns = [{"role": "user", "text": f"turn {i} " + "w" * 120} for i in range(600)]
    call = {"id": 173415, "bot_name": "Test Call Agent", "transcript": turns}
    parsed = json.loads(_trim({"call_log_data": [call], "total_records": 1}).text)
    (kept,) = parsed["call_log_data"]
    assert kept["id"] == 173415
    assert 1 <= len(kept["transcript"]) < 600
    assert "truncated" in parsed["_note"]


def test_a_cut_list_result_stays_valid_json() -> None:
    payload = {"bots": [{"id": i, "prompt": "x" * 500} for i in range(200)], "total_records": 200}
    parsed = json.loads(_trim(payload).text)
    assert 1 <= len(parsed["bots"]) < 200
    assert "of 200 items" in parsed["_note"]
