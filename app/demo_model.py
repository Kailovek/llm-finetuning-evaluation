import json
from time import perf_counter


def infer(prompt: str) -> tuple[str, dict, float]:
    started = perf_counter()
    lowered = prompt.lower()
    if any(term in lowered for term in ("过流", "overcurrent")):
        category, action, risk = "overcurrent", "check_load_and_wiring", "high"
    elif any(term in lowered for term in ("过压", "overvoltage")):
        category, action, risk = "overvoltage", "check_deceleration_and_braking", "high"
    elif any(term in lowered for term in ("丢失", "timeout", "通信")):
        category, action, risk = "communication", "check_power_connection_and_timeout", "medium"
    else:
        category, action, risk = "unknown", "collect_more_evidence", "unknown"
    structured = {"category": category, "action": action, "risk": risk}
    text = json.dumps(structured, ensure_ascii=False)
    return text, structured, round((perf_counter() - started) * 1000, 4)
