from datetime import datetime
from math import floor, sqrt


def commit_frequency_consistency_score(commit_timestamps: list[datetime], eval_now: datetime) -> int:
    """
    Calculate a consistency score (0-100) based on commit frequency distribution.

    This is a pure, deterministic function with no I/O or side effects.

    Algorithm (frozen spec):
    - Only commits within last 84 days count (0 <= age < 84)
    - 12 rolling 7-day bins anchored at eval_now
    - Bin by: age_days = floor((eval_now - ts).total_seconds() / 86400), bin_index = age_days // 7
    - Population standard deviation (divide by 12)
    - cv = std/mean (if mean == 0 → return 0)
    - Score = round(100 * max(0, 1 - min(cv, 2)/2))

    Args:
        commit_timestamps: List of commit timestamps to analyze
        eval_now: Reference datetime for evaluation (typically current time)

    Returns:
        int: Consistency score from 0-100, where:
            - 0 = no commits or highly inconsistent (cv >= 2)
            - 100 = perfectly consistent commit frequency (cv = 0)
            - Linear decay between cv 0 and 2

    Examples:
        >>> from datetime import datetime, timedelta
        >>> eval = datetime(2026, 2, 28, 12, 0, 0)
        >>> # No commits
        >>> commit_frequency_consistency_score([], eval)
        0
        >>> # Perfect consistency: 2 commits/week for 12 weeks
        >>> commits = []
        >>> for week in range(12):
        ...     commits.append(eval - timedelta(days=week*7, hours=1))
        ...     commits.append(eval - timedelta(days=week*7, hours=12))
        >>> commit_frequency_consistency_score(commits, eval)
        100

    Determinism:
        - No randomness, no I/O, no system calls
        - Same inputs always produce same output
        - Safe for parallel execution
        - Thread-safe (no shared state)
    """
    # Initialize 12 bins (each represents a 7-day period)
    bins = [0] * 12

    # Filter and bin commits
    for ts in commit_timestamps:
        # Calculate age in days
        age_seconds = (eval_now - ts).total_seconds()
        age_days = floor(age_seconds / 86400)

        # Only count commits within [0, 84) days
        if 0 <= age_days < 84:
            bin_index = age_days // 7
            # Ensure bin_index is within valid range
            if 0 <= bin_index < 12:
                bins[bin_index] += 1

    # Calculate mean commits per bin
    mean = sum(bins) / 12

    # If no commits (mean == 0), return 0
    if mean == 0:
        return 0

    # Calculate population standard deviation
    variance = sum((count - mean) ** 2 for count in bins) / 12
    std = sqrt(variance)

    # Calculate coefficient of variation
    cv = std / mean

    # Calculate score using frozen formula
    # Score = round(100 * max(0, 1 - min(cv, 2)/2))
    score = 100 * max(0, 1 - min(cv, 2) / 2)

    return round(score)
