def overall_repo_score(
    recency: int,
    frequency: int,
    test_presence: int,
    contributor_distribution: int,
    release_tag_regularity: int,
) -> int:
    """
    Compute the weighted overall repository health score (0-100).

    This is a pure, deterministic function with no I/O or side effects.

    Weights (sum to 1.0):
        recency                 * 0.25
        frequency               * 0.20
        test_presence           * 0.20
        contributor_distribution* 0.20
        release_tag_regularity  * 0.15

    Args:
        recency: Score from commit_recency_score() — 0 to 100
        frequency: Score from commit_frequency_consistency_score() — 0 to 100
        test_presence: Score from test_presence_ratio_score() — 0 to 100
        contributor_distribution: Score from contributor_distribution_score() — 0 to 100
        release_tag_regularity: Score from release_tag_regularity_score() — 0 to 100

    Returns:
        int: Weighted overall score from 0 to 100

    Determinism:
        - No randomness, no I/O, no system calls
        - Same inputs always produce same output
    """
    return round(
        recency * 0.25
        + frequency * 0.20
        + test_presence * 0.20
        + contributor_distribution * 0.20
        + release_tag_regularity * 0.15
    )
