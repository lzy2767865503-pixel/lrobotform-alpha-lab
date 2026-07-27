from __future__ import annotations

import csv
import json
from pathlib import Path

from .generator import SimulationResult
from .models import Questionnaire


def write_csv(
    path: str | Path,
    questionnaire: Questionnaire,
    result: SimulationResult,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    provenance_fields = ["synthetic_record_id", "data_origin", "simulation_seed"]
    fieldnames = provenance_fields + [
        question.id for question in questionnaire.questions
    ]
    with destination.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, row in enumerate(result.rows, start=1):
            writer.writerow(
                {
                    "synthetic_record_id": f"SIM-{index:06d}",
                    "data_origin": "synthetic_simulation",
                    "simulation_seed": result.seed,
                    **row,
                }
            )


def write_report(
    path: str | Path,
    questionnaire: Questionnaire,
    result: SimulationResult,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "product": "Lrobotform Alpha Lab",
        "owner": "LAI ZEYU",
        "purpose": "Authorized questionnaire reliability simulation",
        "questionnaire": {
            "title": questionnaire.title,
            "question_count": len(questionnaire.questions),
            "scale_question_count": len(questionnaire.scale_questions),
        },
        "simulation": result.summary(),
        "notice": (
            "Synthetic local test data only. This report does not represent "
            "human participants and was not submitted to Google Forms."
        ),
    }
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
