from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SUPPORTED_TYPES = {
    "linear_scale",
    "likert",
    "single_choice",
    "checkbox",
    "short_text",
    "paragraph",
}


@dataclass(frozen=True)
class Question:
    id: str
    title: str
    type: str
    options: tuple[str, ...] = ()
    required: bool = False
    ordered: bool = False
    weights: tuple[float, ...] = ()

    @property
    def is_scale(self) -> bool:
        return self.type in {"linear_scale", "likert"} and len(self.options) >= 3

    @classmethod
    def from_dict(cls, raw: dict[str, Any], index: int) -> "Question":
        question_id = str(raw.get("id") or f"Q{index + 1}").strip()
        title = str(raw.get("title") or question_id).strip()
        question_type = str(raw.get("type") or "single_choice").strip().lower()
        aliases = {
            "scale": "linear_scale",
            "linear": "linear_scale",
            "radio": "single_choice",
            "multiple_choice": "single_choice",
            "checkboxes": "checkbox",
            "text": "short_text",
            "long_text": "paragraph",
        }
        question_type = aliases.get(question_type, question_type)
        if question_type not in SUPPORTED_TYPES:
            raise ValueError(f"Unsupported question type: {question_type}")

        options = tuple(str(item).strip() for item in raw.get("options", []) if str(item).strip())
        if question_type in {"linear_scale", "likert", "single_choice", "checkbox"} and not options:
            raise ValueError(f"{question_id} requires at least one option")
        if question_type in {"linear_scale", "likert"} and len(options) < 3:
            raise ValueError(f"{question_id} requires at least three ordered scale options")

        raw_weights = tuple(float(item) for item in raw.get("weights", []) or ())
        if raw_weights and len(raw_weights) != len(options):
            raise ValueError(f"{question_id} weights must match its option count")
        if raw_weights and any(item < 0 for item in raw_weights):
            raise ValueError(f"{question_id} weights cannot be negative")

        return cls(
            id=question_id,
            title=title,
            type=question_type,
            options=options,
            required=bool(raw.get("required", False)),
            ordered=bool(raw.get("ordered", question_type in {"linear_scale", "likert"})),
            weights=raw_weights,
        )


@dataclass(frozen=True)
class Questionnaire:
    title: str
    questions: tuple[Question, ...] = field(default_factory=tuple)

    @property
    def scale_questions(self) -> tuple[Question, ...]:
        return tuple(question for question in self.questions if question.is_scale)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Questionnaire":
        title = str(raw.get("title") or "Untitled questionnaire").strip()
        questions = tuple(
            Question.from_dict(question, index)
            for index, question in enumerate(raw.get("questions", []))
        )
        if not questions:
            raise ValueError("Questionnaire must contain at least one question")
        ids = [question.id for question in questions]
        if len(ids) != len(set(ids)):
            raise ValueError("Question IDs must be unique")
        return cls(title=title, questions=questions)
