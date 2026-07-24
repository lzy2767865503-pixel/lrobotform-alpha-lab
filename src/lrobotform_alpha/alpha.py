from __future__ import annotations

from collections.abc import Iterable, Sequence


def sample_variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def cronbach_alpha(matrix: Iterable[Sequence[float]]) -> float | None:
    rows = [tuple(float(value) for value in row) for row in matrix]
    if len(rows) < 2:
        return None
    width = min((len(row) for row in rows), default=0)
    if width < 2:
        return None

    rows = [row[:width] for row in rows]
    item_variances = [
        sample_variance([row[column] for row in rows])
        for column in range(width)
    ]
    totals = [sum(row) for row in rows]
    total_variance = sample_variance(totals)
    if total_variance <= 0:
        return None

    alpha = width / (width - 1) * (1 - sum(item_variances) / total_variance)
    return max(-1.0, min(1.0, alpha))
