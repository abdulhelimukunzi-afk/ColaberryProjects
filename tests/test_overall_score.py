# tests/test_overall_score.py
from execution.scoring.overall import overall_repo_score


def test_all_zeros():
    assert overall_repo_score(0, 0, 0, 0, 0) == 0


def test_all_hundreds():
    assert overall_repo_score(100, 100, 100, 100, 100) == 100


def test_mixed_values():
    expected = round(100 * 0.25 + 50 * 0.20 + 0 * 0.20 + 100 * 0.20 + 0 * 0.15)
    assert overall_repo_score(100, 50, 0, 100, 0) == expected
