import pytest
from datetime import datetime, timedelta
from execution.scoring.recency import commit_recency_score


class TestCommitRecencyScore:
    """Unit tests for commit_recency_score function"""

    def test_none_latest_commit_returns_zero(self):
        """Test that None latest_commit_timestamp returns 0"""
        eval_now = datetime(2026, 2, 23, 12, 0, 0)
        result = commit_recency_score(None, eval_now)
        assert result == 0

    def test_seven_days_ago_returns_92(self):
        """Test that a commit 7 days ago returns 92"""
        eval_now = datetime(2026, 2, 23, 12, 0, 0)
        latest_commit = eval_now - timedelta(days=7)
        result = commit_recency_score(latest_commit, eval_now)
        assert result == 92

    def test_future_timestamp_returns_100(self):
        """Test that future timestamp (eval_now earlier than latest_commit) returns 100"""
        eval_now = datetime(2026, 2, 23, 12, 0, 0)
        latest_commit = eval_now + timedelta(days=5)  # 5 days in the future
        result = commit_recency_score(latest_commit, eval_now)
        assert result == 100

    def test_zero_days_returns_100(self):
        """Test that same timestamp (0 days) returns 100"""
        eval_now = datetime(2026, 2, 23, 12, 0, 0)
        latest_commit = eval_now
        result = commit_recency_score(latest_commit, eval_now)
        assert result == 100

    def test_ninety_days_or_more_returns_zero(self):
        """Test that 90 days or more returns 0"""
        eval_now = datetime(2026, 2, 23, 12, 0, 0)

        # Exactly 90 days
        latest_commit = eval_now - timedelta(days=90)
        result = commit_recency_score(latest_commit, eval_now)
        assert result == 0

        # More than 90 days
        latest_commit = eval_now - timedelta(days=100)
        result = commit_recency_score(latest_commit, eval_now)
        assert result == 0

    def test_boundary_45_days(self):
        """Test midpoint at 45 days"""
        eval_now = datetime(2026, 2, 23, 12, 0, 0)
        latest_commit = eval_now - timedelta(days=45)
        result = commit_recency_score(latest_commit, eval_now)
        # 100 * (1 - 45/90) = 100 * 0.5 = 50
        assert result == 50

    def test_one_day_ago(self):
        """Test that 1 day ago returns 99"""
        eval_now = datetime(2026, 2, 23, 12, 0, 0)
        latest_commit = eval_now - timedelta(days=1)
        result = commit_recency_score(latest_commit, eval_now)
        # 100 * (1 - 1/90) = 98.888... → rounds to 99
        assert result == 99

    def test_deterministic_behavior(self):
        """Test that same inputs always produce same output (determinism)"""
        eval_now = datetime(2026, 2, 23, 12, 0, 0)
        latest_commit = datetime(2026, 2, 16, 12, 0, 0)

        # Call multiple times
        result1 = commit_recency_score(latest_commit, eval_now)
        result2 = commit_recency_score(latest_commit, eval_now)
        result3 = commit_recency_score(latest_commit, eval_now)

        assert result1 == result2 == result3
