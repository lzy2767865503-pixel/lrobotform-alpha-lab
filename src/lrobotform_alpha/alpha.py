from __future__ import annotations

from collections.abc import Iterable, Sequence


def sample_variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _sample_variance_from_sums(count: int, total: float, squares: float) -> float:
    if count < 2:
        return 0.0
    numerator = squares - (total * total / count)
    return max(0.0, numerator / (count - 1))


def cronbach_alpha(matrix: Iterable[Sequence[float]]) -> float | None:
    rows = [tuple(float(value) for value in row) for row in matrix]
    if len(rows) < 2:
        return None
    width = min((len(row) for row in rows), default=0)
    if width < 2:
        return None

    rows = [row[:width] for row in rows]
    column_totals = [0.0] * width
    column_squares = [0.0] * width
    score_total = 0.0
    score_squares = 0.0
    for row in rows:
        score = 0.0
        for column, value in enumerate(row):
            column_totals[column] += value
            column_squares[column] += value * value
            score += value
        score_total += score
        score_squares += score * score

    row_count = len(rows)
    item_variances = [
        _sample_variance_from_sums(
            row_count,
            column_totals[column],
            column_squares[column],
        )
        for column in range(width)
    ]
    total_variance = _sample_variance_from_sums(
        row_count,
        score_total,
        score_squares,
    )
    if total_variance <= 0:
        return None

    alpha = width / (width - 1) * (1 - sum(item_variances) / total_variance)
    return max(-1.0, min(1.0, alpha))
