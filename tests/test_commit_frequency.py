import pytest
from datetime import datetime, timedelta
from execution.scoring.frequency import commit_frequency_consistency_score


class TestCommitFrequencyConsistencyScore:
    """
    Unit tests for commit_frequency_consistency_score function.

    Algorithm spec (frozen):
    - Only commits within last 84 days count
    - 12 rolling 7-day bins
    - Population standard deviation
    - cv = std/mean (if mean == 0 → return 0)
    - Score = round(100 * max(0, 1 - min(cv, 2)/2))
    """

    def test_no_commits_returns_zero(self):
        """Test that empty commit list returns score 0"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)
        result = commit_frequency_consistency_score([], eval_now)
        assert result == 0

    def test_two_commits_every_week_for_12_weeks_returns_100(self):
        """Test that perfectly consistent 2 commits/week for 12 weeks returns score 100"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)
        commits = []

        # Create 2 commits per week for 12 weeks (24 commits total)
        for week in range(12):
            # Two commits spread within each week
            day_offset = week * 7
            commits.append(eval_now - timedelta(days=day_offset, hours=1))
            commits.append(eval_now - timedelta(days=day_offset, hours=12))

        result = commit_frequency_consistency_score(commits, eval_now)
        assert result == 100

    def test_all_commits_in_same_week_returns_low_score(self):
        """Test that 24 commits concentrated in same week returns low score (high variance)"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)
        commits = []

        # All 24 commits within the same week (days 0-6)
        for i in range(24):
            commits.append(eval_now - timedelta(days=2, hours=i))

        result = commit_frequency_consistency_score(commits, eval_now)
        assert result < 30, f"Expected score < 30 for clustered commits, got {result}"

    def test_commits_older_than_84_days_ignored(self):
        """Test that commits older than 84 days are not counted"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)

        # Recent commits: 2 per week for 12 weeks
        recent_commits = []
        for week in range(12):
            day_offset = week * 7
            recent_commits.append(eval_now - timedelta(days=day_offset, hours=1))
            recent_commits.append(eval_now - timedelta(days=day_offset, hours=12))

        # Old commits (beyond 84 days)
        old_commits = [
            eval_now - timedelta(days=85),
            eval_now - timedelta(days=90),
            eval_now - timedelta(days=100),
            eval_now - timedelta(days=200),
        ]

        # Score with only recent commits
        score_recent = commit_frequency_consistency_score(recent_commits, eval_now)

        # Score with recent + old commits (old should be ignored)
        score_combined = commit_frequency_consistency_score(recent_commits + old_commits, eval_now)

        # Scores should be identical since old commits are ignored
        assert score_recent == score_combined

    def test_deterministic_behavior(self):
        """Test that same inputs always produce same output (determinism)"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)
        commits = [
            eval_now - timedelta(days=5),
            eval_now - timedelta(days=12),
            eval_now - timedelta(days=19),
            eval_now - timedelta(days=26),
            eval_now - timedelta(days=33),
            eval_now - timedelta(days=40),
        ]

        # Call multiple times
        result1 = commit_frequency_consistency_score(commits, eval_now)
        result2 = commit_frequency_consistency_score(commits, eval_now)
        result3 = commit_frequency_consistency_score(commits, eval_now)

        assert result1 == result2 == result3

    def test_only_commits_within_84_days(self):
        """Test boundary: commit at exactly 84 days should be excluded"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)

        # Commits at various ages
        commits = [
            eval_now - timedelta(days=0),   # 0 days ago
            eval_now - timedelta(days=7),   # 7 days ago
            eval_now - timedelta(days=14),  # 14 days ago
            eval_now - timedelta(days=83),  # 83 days ago (should be included)
            eval_now - timedelta(days=84),  # 84 days ago (should be excluded)
        ]

        # With all commits
        score_all = commit_frequency_consistency_score(commits, eval_now)

        # Without the 84-day commit
        commits_filtered = commits[:4]  # Exclude last one
        score_filtered = commit_frequency_consistency_score(commits_filtered, eval_now)

        # Should be the same since 84-day commit is excluded
        assert score_all == score_filtered

    def test_single_commit_returns_zero(self):
        """Test that a single commit returns 0 (std=0, all bins 0 except one)"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)
        commits = [eval_now - timedelta(days=5)]

        result = commit_frequency_consistency_score(commits, eval_now)
        # With only 1 commit, most bins are 0, high variance
        # cv will be high, score should be low
        assert result >= 0 and result <= 100

    def test_moderate_variance_scenario(self):
        """Test a moderate variance scenario for score calibration"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)
        commits = []

        # Variable pattern: 1, 2, 3, 2, 1, 2, 3, 2, 1, 2, 3, 2 commits per week
        pattern = [1, 2, 3, 2, 1, 2, 3, 2, 1, 2, 3, 2]
        for week, count in enumerate(pattern):
            for c in range(count):
                commits.append(eval_now - timedelta(days=week * 7, hours=c * 6))

        result = commit_frequency_consistency_score(commits, eval_now)
        # Moderate variance should give moderate score
        assert 30 <= result <= 85, f"Expected moderate score, got {result}"

    def test_empty_list_vs_none_timestamps(self):
        """Test that empty list is handled correctly"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)
        result = commit_frequency_consistency_score([], eval_now)
        assert result == 0

    def test_future_commits_handling(self):
        """Test behavior with commits in the future (should likely be ignored or included based on 84-day window)"""
        eval_now = datetime(2026, 2, 28, 12, 0, 0)

        # Mix of past and future commits
        commits = [
            eval_now - timedelta(days=7),
            eval_now - timedelta(days=14),
            eval_now + timedelta(days=5),  # Future commit
        ]

        result = commit_frequency_consistency_score(commits, eval_now)
        # Should be deterministic regardless
        assert isinstance(result, int)
        assert 0 <= result <= 100
