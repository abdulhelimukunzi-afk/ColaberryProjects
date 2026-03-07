import pytest
from execution.scoring.contributor_distribution import contributor_distribution_score


class TestContributorDistributionScore:
    """
    Unit tests for contributor_distribution_score function.

    Algorithm (inferred from spec):
    - Empty list or single contributor → score 0
    - Calculate largest contributor's share
    - Score based on diversity: higher diversity = higher score
    """

    def test_empty_list_returns_zero(self):
        """Test that empty list returns score 0"""
        result = contributor_distribution_score([])
        assert result == 0

    def test_single_contributor_returns_zero(self):
        """Test that single contributor (no diversity) returns score 0"""
        author_ids = ["a", "a", "a", "a"]
        result = contributor_distribution_score(author_ids)
        assert result == 0

    def test_two_contributors_equal_returns_50(self):
        """Test that two contributors with equal contributions returns score 50"""
        author_ids = ["a", "a", "b", "b"]
        result = contributor_distribution_score(author_ids)
        assert result == 50

    def test_dominant_contributor_returns_20(self):
        """Test that dominant contributor (80% share) returns score 20"""
        author_ids = ["a", "a", "a", "a", "b"]
        result = contributor_distribution_score(author_ids)
        assert result == 20

    def test_even_distribution_many_contributors_returns_75(self):
        """Test that even distribution across 4 contributors returns score 75"""
        author_ids = ["a", "b", "c", "d"]
        result = contributor_distribution_score(author_ids)
        assert result == 75

    def test_deterministic_behavior(self):
        """Test that same inputs produce same output (determinism)"""
        author_ids = ["a", "a", "b", "c", "c", "d"]

        # Call multiple times
        result1 = contributor_distribution_score(author_ids)
        result2 = contributor_distribution_score(author_ids)
        result3 = contributor_distribution_score(author_ids)

        assert result1 == result2 == result3

    def test_large_dataset_stability_returns_20(self):
        """Test large dataset with dominant contributor (80% share) returns score 20"""
        author_ids = ["a"] * 80 + ["b"] * 10 + ["c"] * 10
        result = contributor_distribution_score(author_ids)
        assert result == 20

    def test_three_contributors_unequal(self):
        """Test three contributors with unequal distribution"""
        # a: 50%, b: 30%, c: 20%
        author_ids = ["a"] * 5 + ["b"] * 3 + ["c"] * 2
        result = contributor_distribution_score(author_ids)
        # Largest share = 5/10 = 0.5
        # Expected: 100 * (1 - 0.5) = 50
        assert result == 50

    def test_perfect_distribution_five_contributors(self):
        """Test perfect distribution across 5 contributors"""
        author_ids = ["a", "b", "c", "d", "e"]
        result = contributor_distribution_score(author_ids)
        # Largest share = 1/5 = 0.2
        # Expected: 100 * (1 - 0.2) = 80
        assert result == 80

    def test_ten_contributors_equal(self):
        """Test equal distribution across 10 contributors"""
        author_ids = []
        for i in range(10):
            author_ids.append(str(i))
        result = contributor_distribution_score(author_ids)
        # Largest share = 1/10 = 0.1
        # Expected: 100 * (1 - 0.1) = 90
        assert result == 90

    def test_one_commit_per_contributor(self):
        """Test scenario with one commit per contributor"""
        author_ids = ["alice", "bob", "charlie"]
        result = contributor_distribution_score(author_ids)
        # Largest share = 1/3 ≈ 0.333
        # Expected: 100 * (1 - 1/3) ≈ 66.67 → rounds to 67
        assert result == 67

    def test_order_does_not_matter(self):
        """Test that order of author IDs doesn't affect score"""
        author_ids_1 = ["a", "b", "a", "c", "b"]
        author_ids_2 = ["b", "a", "c", "a", "b"]
        author_ids_3 = ["c", "b", "b", "a", "a"]

        result1 = contributor_distribution_score(author_ids_1)
        result2 = contributor_distribution_score(author_ids_2)
        result3 = contributor_distribution_score(author_ids_3)

        assert result1 == result2 == result3

    def test_empty_string_author_ids(self):
        """Test handling of empty string author IDs"""
        author_ids = ["", "", "a", "a"]
        result = contributor_distribution_score(author_ids)
        # Two contributors: "" with 2 commits, "a" with 2 commits
        # Largest share = 2/4 = 0.5
        assert result == 50

    def test_single_commit(self):
        """Test single commit returns 0 (only one contributor)"""
        author_ids = ["alice"]
        result = contributor_distribution_score(author_ids)
        assert result == 0
