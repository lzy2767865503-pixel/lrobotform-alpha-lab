from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass
from typing import Any

from .alpha import cronbach_alpha
from .models import Question, Questionnaire


@dataclass(frozen=True)
class SimulationResult:
    rows: tuple[dict[str, str], ...]
    alpha: float | None
    target_min: float
    target_max: float
    seed: int
    attempts: int
    scale_question_ids: tuple[str, ...]
    distributions: dict[str, dict[str, int]]

    @property
    def alpha_passed(self) -> bool:
        return self.alpha is None or self.target_min <= self.alpha <= self.target_max

    def summary(self) -> dict[str, Any]:
        return {
            "responses": len(self.rows),
            "alpha": round(self.alpha, 4) if self.alpha is not None else None,
            "target": [self.target_min, self.target_max],
            "alpha_passed": self.alpha_passed,
            "seed": self.seed,
            "attempts": self.attempts,
            "scale_question_ids": list(self.scale_question_ids),
            "distributions": self.distributions,
        }


def _weighted_choice(options: tuple[str, ...], weights: tuple[float, ...], rng: random.Random) -> str:
    if not options:
        return ""
    if weights and sum(weights) > 0:
        return rng.choices(options, weights=weights, k=1)[0]
    return options[rng.randrange(len(options))]


def _normal_choice(options: tuple[str, ...], rng: random.Random) -> str:
    if not options:
        return ""
    center = (len(options) - 1) / 2
    sigma = max(0.65, len(options) / 3.4)
    index = round(rng.gauss(center, sigma))
    return options[max(0, min(len(options) - 1, index))]


def _scale_matrix(
    questions: tuple[Question, ...],
    response_count: int,
    seed: int,
    target_min: float,
    target_max: float,
) -> tuple[list[list[int]], float | None, int]:
    if len(questions) < 2 or response_count < 3:
        return [], None, 0

    target = (target_min + target_max) / 2
    item_count = len(questions)
    average_correlation = target / (item_count - target * (item_count - 1))
    average_correlation = max(0.05, min(0.95, average_correlation))
    base_loading = math.sqrt(average_correlation)
    best: tuple[float, list[list[int]], float, int] | None = None

    for attempt in range(1, 121):
        rng = random.Random(seed + attempt * 7919)
        adjustment = 0.62 + ((attempt - 1) % 30) * 0.027
        loading = max(0.12, min(0.96, base_loading / adjustment))
        noise = math.sqrt(max(0.001, 1 - loading**2))
        matrix: list[list[int]] = []

        for _ in range(response_count):
            latent = rng.gauss(0, 1)
            row: list[int] = []
            for item_index, question in enumerate(questions):
                item_bias = ((item_index % 5) - 2) * 0.07
                continuous = loading * latent + noise * rng.gauss(0, 1) + item_bias
                probability = 1 / (1 + math.exp(-continuous))
                option_index = round(probability * (len(question.options) - 1))
                row.append(max(0, min(len(question.options) - 1, option_index)) + 1)
            matrix.append(row)

        alpha = cronbach_alpha(matrix)
        if alpha is None:
            continue
        distance = 0.0 if target_min <= alpha <= target_max else min(
            abs(alpha - target_min),
            abs(alpha - target_max),
        )
        candidate = (distance, matrix, alpha, attempt)
        if best is None or (candidate[0], abs(alpha - target)) < (best[0], abs(best[2] - target)):
            best = candidate
        if target_min <= alpha <= target_max and abs(alpha - target) <= 0.025:
            break

    if best is None:
        raise RuntimeError("Unable to generate a non-degenerate scale matrix")
    return best[1], best[2], best[3]


def _response_for_question(
    question: Question,
    response_index: int,
    rng: random.Random,
) -> str:
    if question.type == "single_choice":
        if question.weights:
            return _weighted_choice(question.options, question.weights, rng)
        return _normal_choice(question.options, rng) if question.ordered else _weighted_choice(
            question.options,
            (),
            rng,
        )
    if question.type == "checkbox":
        count = min(len(question.options), max(1, round(abs(rng.gauss(1.35, 0.65)))))
        values = rng.sample(list(question.options), count)
        return "; ".join(values)
    if question.type in {"short_text", "paragraph"}:
        return f"Synthetic test response {response_index + 1:03d}"
    return ""


def simulate(
    questionnaire: Questionnaire,
    response_count: int = 100,
    seed: int = 20260724,
    target_min: float = 0.7,
    target_max: float = 0.9,
) -> SimulationResult:
    if not 3 <= response_count <= 10000:
        raise ValueError("response_count must be between 3 and 10000")
    if not 0 < target_min <= target_max < 1:
        raise ValueError("Alpha target must satisfy 0 < min <= max < 1")

    scale_questions = questionnaire.scale_questions
    scale_matrix, alpha, attempts = _scale_matrix(
        scale_questions,
        response_count,
        seed,
        target_min,
        target_max,
    )
    scale_positions = {
        question.id: index for index, question in enumerate(scale_questions)
    }
    rows: list[dict[str, str]] = []

    for response_index in range(response_count):
        rng = random.Random(seed + response_index * 1009)
        row: dict[str, str] = {}
        for question in questionnaire.questions:
            if question.id in scale_positions and scale_matrix:
                column = scale_positions[question.id]
                option_index = scale_matrix[response_index][column] - 1
                row[question.id] = question.options[option_index]
            else:
                row[question.id] = _response_for_question(
                    question,
                    response_index,
                    rng,
                )
        rows.append(row)

    distributions: dict[str, dict[str, int]] = {}
    for question in questionnaire.questions:
        counts = Counter(row[question.id] for row in rows)
        distributions[question.id] = dict(sorted(counts.items()))

    return SimulationResult(
        rows=tuple(rows),
        alpha=alpha,
        target_min=target_min,
        target_max=target_max,
        seed=seed,
        attempts=attempts,
        scale_question_ids=tuple(question.id for question in scale_questions),
        distributions=distributions,
    )
