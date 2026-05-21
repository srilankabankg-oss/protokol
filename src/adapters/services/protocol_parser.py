"""Protocol parser — converts free-text meeting notes to tabular protocol_data."""
import re
from typing import Any


SECTION_PATTERNS = {
    "heard": re.compile(r"##?\s*СЛУШАЛИ\s*\n(.*?)(?=##?\s*ВЫСТУПИЛИ|##?\s*ПОСТАНОВИЛИ|\Z)", re.DOTALL),
    "spoke": re.compile(r"##?\s*ВЫСТУПИЛИ\s*\n(.*?)(?=##?\s*ПОСТАНОВИЛИ|\Z)", re.DOTALL),
    "decided": re.compile(r"##?\s*ПОСТАНОВИЛИ\s*\n(.*?)(?=##?\s*СЛУШАЛИ|\Z)", re.DOTALL),
}


def _extract_list_items(text: str) -> list[str]:
    items = re.findall(r"(?:^|\n)\s*(?:-\s*|\d+\.\s*)(.*?)(?=\n\s*(?:-\s*|\d+\.\s*)|\Z)", text, re.DOTALL)
    if not items:
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        return lines
    return [item.strip() for item in items]


def _parse_speaker_topic(items: list[str]) -> list[dict]:
    result = []
    for item in items:
        speaker_match = re.match(r"^(.+?)\s*[–—]\s*(.+)$", item)
        if speaker_match:
            result.append({"speaker": speaker_match.group(1).strip(), "topic": speaker_match.group(2).strip()})
        else:
            result.append({"speaker": "", "topic": item})
    return result


def _parse_decisions(items: list[str]) -> list[dict]:
    result = []
    for item in items:
        entry: dict = {"task": item, "responsible": "", "deadline": ""}
        resp_match = re.search(r"(?:отв(?:\.|етственный)?|responsible?|исполнитель)\s*[–—:]\s*(.+?)(?:\.|$|\n)", item, re.IGNORECASE)
        if resp_match:
            entry["responsible"] = resp_match.group(1).strip()
        deadline_match = re.search(r"(?:срок|deadline|до)\s*[–—:]\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", item, re.IGNORECASE)
        if deadline_match:
            entry["deadline"] = deadline_match.group(1)
        result.append(entry)
    return result


async def parse_notes_to_protocol(markdown_text: str, use_llm: bool = False) -> dict[str, Any]:
    protocol_data = {"heard": [], "spoke": [], "decided": []}

    heard_match = SECTION_PATTERNS["heard"].search(markdown_text)
    if heard_match:
        items = _extract_list_items(heard_match.group(1))
        protocol_data["heard"] = _parse_speaker_topic(items)

    spoke_match = SECTION_PATTERNS["spoke"].search(markdown_text)
    if spoke_match:
        items = _extract_list_items(spoke_match.group(1))
        protocol_data["spoke"] = _parse_speaker_topic(items)

    decided_match = SECTION_PATTERNS["decided"].search(markdown_text)
    if decided_match:
        items = _extract_list_items(decided_match.group(1))
        protocol_data["decided"] = _parse_decisions(items)

    if use_llm:
        try:
            from src.infrastructure.llm_gateway import query_llm
            import json
            system_prompt = (
                "Extract meeting data into tabular format. "
                "Map participants to the People table. "
                "Identify action items, responsibilities (RACI), and deadlines. "
                "Output STRICT JSON with keys: heard, spoke, decided. "
                "Each entry must have speaker/topic (heard/spoke) or task/responsible/deadline (decided)."
            )
            llm_response = await query_llm(system_prompt, markdown_text, timeout=60)
            if llm_response:
                try:
                    parsed = json.loads(llm_response)
                    if isinstance(parsed, dict) and all(k in parsed for k in ("heard", "spoke", "decided")):
                        protocol_data = parsed
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

    return protocol_data