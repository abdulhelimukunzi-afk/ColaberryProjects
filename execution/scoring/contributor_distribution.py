def contributor_distribution_score(author_emails: list[str]) -> int:
    """
    Calculate a diversity score (0-100) based on contributor distribution.

    This is a pure, deterministic function with no I/O or side effects.

    Algorithm (frozen spec):
    - Empty list or single contributor → score 0
    - Calculate largest contributor's share of total commits
    - Score = round(100 * max(0, 1 - largest_share))
    - Higher diversity (more even distribution) = higher score

    Args:
        author_emails: List of author identifiers (one per commit)

    Returns:
        int: Distribution score from 0-100, where:
            - 0 = no commits or single contributor (no diversity)
            - 100 = perfectly even distribution (theoretical, approaches as contributors increase)
            - Linear scaling based on largest contributor's share

    Examples:
        >>> contributor_distribution_score([])
        0
        >>> contributor_distribution_score(["a", "a", "a", "a"])
        0
        >>> contributor_distribution_score(["a", "a", "b", "b"])
        50

    Determinism:
        - No randomness, no I/O, no system calls
        - Same inputs always produce same output
        - Safe for parallel execution
        - Thread-safe (no shared state)
    """
    # Handle empty list
    if not author_emails:
        return 0

    # Count commits per author (using dict to avoid external dependencies)
    author_counts = {}
    for author in author_emails:
        author_counts[author] = author_counts.get(author, 0) + 1

    # Get total commits and top contributor's count
    total_commits = len(author_emails)
    top_contributor_commits = max(author_counts.values())

    # Calculate share of top contributor
    share = top_contributor_commits / total_commits

    # Calculate score: 100 * (1 - share), bounded to [0, 100]
    score = 100 * max(0, 1 - share)
    return round(score)
