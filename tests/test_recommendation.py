from app.api.endpoints.search import make_recommendation


def test_great_score():
    assert "Great" in make_recommendation(80, 22)


def test_too_hot():
    assert "too hot" in make_recommendation(90, 36)


def test_too_cold():
    assert "winter" in make_recommendation(80, 4)


def test_moderate():
    assert "Maybe" in make_recommendation(60, 22)


def test_low_temp_edge():
    assert "winter" in make_recommendation(50, 4)


def test_high_temp_edge():
    assert "too hot" in make_recommendation(50, 36)


def test_exactly_5_is_not_cold():
    assert "winter" not in make_recommendation(50, 5)


def test_exactly_35_is_not_hot():
    assert "too hot" not in make_recommendation(50, 35)
