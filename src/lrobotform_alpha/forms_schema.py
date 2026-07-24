from __future__ import annotations

from typing import Any

from .models import Questionnaire


GOOGLE_TYPE_MAP = {
    "MULTIPLE_CHOICE": "single_choice",
    "CHECKBOX": "checkbox",
    "SCALE": "linear_scale",
    "GRID": "likert",
    "CHECKBOX_GRID": "checkbox",
    "TEXT": "short_text",
    "PARAGRAPH_TEXT": "paragraph",
    "LIST": "single_choice",
}


def _scale_options(item: dict[str, Any]) -> list[str]:
    lower = int(item.get("lowerBound", 1))
    upper = int(item.get("upperBound", 5))
    if lower >= upper:
        raise ValueError("Scale lowerBound must be smaller than upperBound")
    return [str(value) for value in range(lower, upper + 1)]


def _question_from_google_item(item: dict[str, Any], index: int) -> list[dict[str, Any]]:
    google_type = str(item.get("type", "")).upper()
    normalized_type = GOOGLE_TYPE_MAP.get(google_type)
    if normalized_type is None:
        return []

    base_id = str(item.get("id") or f"Q{index + 1}")
    title = str(item.get("title") or base_id)
    required = bool(item.get("required", False))

    if google_type == "SCALE":
        options = _scale_options(item)
    else:
        options = [str(value) for value in item.get("choices", []) if str(value).strip()]

    if google_type in {"GRID", "CHECKBOX_GRID"}:
        rows = [str(value) for value in item.get("rows", []) if str(value).strip()]
        columns = [str(value) for value in item.get("columns", []) if str(value).strip()]
        return [
            {
                "id": f"{base_id}_{row_index + 1}",
                "title": f"{title} - {row}",
                "type": "likert" if google_type == "GRID" else "checkbox",
                "options": columns,
                "required": required,
                "ordered": google_type == "GRID",
            }
            for row_index, row in enumerate(rows)
            if columns
        ]

    payload: dict[str, Any] = {
        "id": base_id,
        "title": title,
        "type": normalized_type,
        "required": required,
    }
    if normalized_type in {"linear_scale", "likert", "single_choice", "checkbox"}:
        payload["options"] = options
    if normalized_type in {"linear_scale", "likert"}:
        payload["ordered"] = True
    return [payload]


def questionnaire_from_google_blueprint(raw: dict[str, Any]) -> Questionnaire:
    questions: list[dict[str, Any]] = []
    for index, item in enumerate(raw.get("items", [])):
        questions.extend(_question_from_google_item(item, index))
    return Questionnaire.from_dict(
        {
            "title": raw.get("title") or "Google Forms questionnaire",
            "questions": questions,
        }
    )
