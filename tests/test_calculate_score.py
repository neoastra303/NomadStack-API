from app.api.endpoints.search import calculate_score
from app.schemas.schemas import ScoreBreakdown


def test_calculate_score_ideal():
    s = calculate_score(22, 30)
    assert isinstance(s, ScoreBreakdown)
    assert s.total > 90
    assert s.temperature_score > 90
    assert s.humidity_score > 60


def test_calculate_score_hot():
    s = calculate_score(40, 50)
    assert s.total < 50
    assert s.temperature_score == 28.0
    assert s.humidity_score == 50.0


def test_calculate_score_cold():
    s = calculate_score(0, 60)
    assert s.total == 20.4
    assert s.temperature_weight == 0.7
    assert s.humidity_weight == 0.3


def test_calculate_score_humid():
    s = calculate_score(22, 90)
    assert s.total == 73.0
    assert s.temperature_score == 100.0


def test_calculate_score_bounds():
    s = calculate_score(100, 0)
    assert s.total >= 0
    assert s.total <= 100


def test_calculate_score_negative():
    s = calculate_score(-10, 100)
    assert s.total >= 0
