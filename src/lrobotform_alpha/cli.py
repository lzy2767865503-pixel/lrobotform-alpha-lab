from __future__ import annotations

import argparse
import json
from pathlib import Path

from .forms_schema import questionnaire_from_google_blueprint
from .generator import simulate
from .models import Questionnaire
from .report import write_csv, write_report


def _load_questionnaire(path: str, google_blueprint: bool) -> Questionnaire:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return (
        questionnaire_from_google_blueprint(raw)
        if google_blueprint
        else Questionnaire.from_dict(raw)
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lrobotform-alpha",
        description=(
            "Generate local synthetic questionnaire data and evaluate "
            "Cronbach's Alpha. This command never submits Google Forms."
        ),
    )
    parser.add_argument("schema", help="Questionnaire JSON or Google Forms blueprint JSON")
    parser.add_argument("--google-blueprint", action="store_true")
    parser.add_argument("--responses", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260724)
    parser.add_argument("--target-min", type=float, default=0.7)
    parser.add_argument("--target-max", type=float, default=0.9)
    parser.add_argument("--csv", default="output/synthetic_responses.csv")
    parser.add_argument("--report", default="output/alpha_report.json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    questionnaire = _load_questionnaire(args.schema, args.google_blueprint)
    result = simulate(
        questionnaire,
        response_count=args.responses,
        seed=args.seed,
        target_min=args.target_min,
        target_max=args.target_max,
    )
    write_csv(args.csv, questionnaire, result)
    write_report(args.report, questionnaire, result)
    alpha_text = "not applicable" if result.alpha is None else f"{result.alpha:.4f}"
    print(f"Generated {len(result.rows)} local synthetic rows")
    print(f"Cronbach's Alpha: {alpha_text}")
    print(f"CSV: {args.csv}")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
