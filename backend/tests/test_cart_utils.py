from backend.app.utils import calc_cart_total

import logging


logger = logging.getLogger(__name__)


def test_calc_cart_total_empty():
    items: list[dict[str, object]] = []
    logger.info("calc_cart_total: empty cart -> expect 0.0")
    total = calc_cart_total(items)
    logger.info("result: %s", total)
    assert total == 0.0


def test_calc_cart_total_sums_numbers():
    items = [
        {"line_total": 10},
        {"line_total": 2.5},
        {"line_total": "3.0"},
    ]
    logger.info("calc_cart_total: sum numeric + string values")
    logger.info("items: %s", items)
    total = calc_cart_total(items)
    logger.info("result: %s (expect 15.5)", total)
    assert total == 15.5


def test_calc_cart_total_ignores_missing():
    items = [
        {"title": "x"},
        {"line_total": 1},
        {"line_total": None},
    ]
    logger.info("calc_cart_total: ignore missing/None line_total")
    logger.info("items: %s", items)
    total = calc_cart_total(items)
    logger.info("result: %s (expect 1.0)", total)
    assert total == 1.0

