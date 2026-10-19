import argparse
import json
from pathlib import Path

TEMPLATES = [
    (
        "分析驱动器过流告警",
        "过流告警发生在启动阶段",
        "overcurrent",
        "check_load_and_wiring",
        "high",
    ),
    (
        "分析驱动器过压告警",
        "过压告警发生在减速阶段",
        "overvoltage",
        "check_deceleration_and_braking",
        "high",
    ),
    (
        "分析通信超时",
        "设备通信间歇丢失",
        "communication",
        "check_power_connection_and_timeout",
        "medium",
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic SFT instruction data")
    parser.add_argument("--count", type=int, choices=[100, 1000, 10000], default=100)
    parser.add_argument("--output", type=Path, default=Path("data/generated/demo_sft.jsonl"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for index in range(args.count):
            instruction, input_text, category, action, risk = TEMPLATES[index % len(TEMPLATES)]
            row = {
                "instruction": f"{instruction}（案例 {index + 1}）",
                "input": input_text,
                "output": json.dumps(
                    {"category": category, "action": action, "risk": risk},
                    ensure_ascii=False,
                ),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"generated={args.count} output={args.output}")


if __name__ == "__main__":
    main()
