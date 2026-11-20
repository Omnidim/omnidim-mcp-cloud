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
    return json.loads(text.split("\n\n[")[0])


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
    assert "interactions" in text.split("\n\n[")[1]


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
