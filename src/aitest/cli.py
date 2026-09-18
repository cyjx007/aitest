from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import Case, Evaluator


class EchoAdapter:
    def generate(self, prompt: str) -> str:
        return prompt


def load_cases(path: Path) -> list[Case]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("test file must contain a JSON array")
    return [Case.from_dict(item) for item in payload]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run AI regression tests")
    parser.add_argument("file", nargs="?", type=Path, help="JSON test-case file")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    if args.file is None:
        parser.print_help()
        return 0

    results = Evaluator(EchoAdapter()).run(load_cases(args.file))

    if args.as_json:
        print(json.dumps(
            {"passed": all(r.passed for r in results),
             "results": [r.to_dict() for r in results]},
            indent=2,
            ensure_ascii=False,
        ))
    else:
        for result in results:
            mark = "PASS" if result.passed else "FAIL"
            print(f"[{mark}] {result.case_id}")
            for failure in result.failures:
                print(f"  - {failure}")
        print(f"\n{sum(r.passed for r in results)}/{len(results)} passed")

    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
