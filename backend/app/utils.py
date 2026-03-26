from __future__ import annotations

from typing import Iterable, Mapping


def calc_cart_total(items: Iterable[Mapping[str, object]]) -> float:
    total = 0.0
    for i in items:
        v = i.get("line_total")
        if v is None:
            continue
        total += float(v)
    return total

