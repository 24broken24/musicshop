from app.utils import calc_cart_total


def test_calc_cart_total_empty():
    assert calc_cart_total([]) == 0.0


def test_calc_cart_total_sums_numbers():
    items = [
        {"line_total": 10},
        {"line_total": 2.5},
        {"line_total": "3.0"},
    ]
    assert calc_cart_total(items) == 15.5


def test_calc_cart_total_ignores_missing():
    items = [
        {"title": "x"},
        {"line_total": 1},
        {"line_total": None},
    ]
    assert calc_cart_total(items) == 1.0

