import pytest
from execution.scoring.release_tag_regularity import release_tag_regularity_score


class TestReleaseTagRegularityScore:
    """
    Unit tests for release_tag_regularity_score function.

    Scoring spec (frozen):
    - 0 tags  → 0
    - 1-2 tags → 30
    - 3-5 tags → 60
    - 6+ tags  → 100
    """

    def test_empty_list_returns_zero(self):
        """Test that empty tag list returns score 0"""
        result = release_tag_regularity_score([])
        assert result == 0

    def test_one_tag_returns_30(self):
        """Test that a single tag returns score 30"""
        result = release_tag_regularity_score(["v1.0.0"])
        assert result == 30

    def test_two_tags_returns_30(self):
        """Test that two tags returns score 30"""
        result = release_tag_regularity_score(["v1.0.0", "v1.1.0"])
        assert result == 30

    def test_three_tags_returns_60(self):
        """Test that three tags returns score 60"""
        result = release_tag_regularity_score(["v1", "v2", "v3"])
        assert result == 60

    def test_five_tags_returns_60(self):
        """Test that five tags returns score 60"""
        result = release_tag_regularity_score(["v1", "v2", "v3", "v4", "v5"])
        assert result == 60

    def test_six_tags_returns_100(self):
        """Test that six tags returns score 100"""
        result = release_tag_regularity_score(["v1", "v2", "v3", "v4", "v5", "v6"])
        assert result == 100

    def test_deterministic_behavior(self):
        """Test that same inputs produce same output (determinism)"""
        tags = ["v1.0", "v1.1", "v2.0", "v2.1"]

        result1 = release_tag_regularity_score(tags)
        result2 = release_tag_regularity_score(tags)

        assert result1 == result2

    def test_more_than_six_tags_returns_100(self):
        """Test that more than six tags also returns score 100"""
        tags = ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10"]
        result = release_tag_regularity_score(tags)
        assert result == 100

    def test_four_tags_returns_60(self):
        """Test that four tags (boundary within 3-5 range) returns score 60"""
        result = release_tag_regularity_score(["v1.0", "v1.1", "v1.2", "v1.3"])
        assert result == 60

    def test_tag_names_do_not_affect_score(self):
        """Test that tag name content does not affect score, only count matters"""
        tags_semver = ["v1.0.0", "v1.1.0", "v2.0.0"]
        tags_simple = ["a", "b", "c"]
        tags_arbitrary = ["release-2026-01", "release-2026-02", "release-2026-03"]

        assert release_tag_regularity_score(tags_semver) == 60
        assert release_tag_regularity_score(tags_simple) == 60
        assert release_tag_regularity_score(tags_arbitrary) == 60
