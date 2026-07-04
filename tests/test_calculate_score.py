from app.api.endpoints.search import calculate_score


def test_calculate_score_ideal():
    score = calculate_score(22, 30)
    assert score > 90


def test_calculate_score_hot():
    score = calculate_score(40, 50)
    assert score < 50


def test_calculate_score_cold():
    score = calculate_score(0, 60)
    assert score == 20.4


def test_calculate_score_humid():
    score = calculate_score(22, 90)
    assert score == 73.0
