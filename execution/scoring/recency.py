from datetime import datetime
from math import floor


def commit_recency_score(latest_commit_timestamp: datetime | None, eval_now: datetime) -> int:
    """
    Calculate a recency score (0-100) based on how recently the last commit occurred.

    This is a pure, deterministic function with no I/O or side effects.

    Algorithm:
    - If no commit timestamp exists, returns 0 (no activity)
    - Computes days between eval_now and latest_commit_timestamp
    - Clamps days to be non-negative (future commits treated as days=0)
    - Linear decay from 100 (≤0 days) to 0 (≥90 days)

    Args:
        latest_commit_timestamp: The timestamp of the most recent commit, or None if no commits
        eval_now: The reference datetime for evaluation (typically current time)

    Returns:
        int: Score from 0-100, where:
            - 0 = no commits or ≥90 days old
            - 100 = ≤0 days old (same day or future)
            - Linear interpolation between 0-90 days

    Examples:
        >>> from datetime import datetime, timedelta
        >>> eval = datetime(2026, 2, 23, 12, 0, 0)
        >>> commit_recency_score(None, eval)
        0
        >>> commit_recency_score(eval - timedelta(days=7), eval)
        92
        >>> commit_recency_score(eval + timedelta(days=5), eval)
        100
        >>> commit_recency_score(eval - timedelta(days=45), eval)
        50
        >>> commit_recency_score(eval - timedelta(days=90), eval)
        0

    Determinism:
        - No randomness, no I/O, no system calls
        - Same inputs always produce same output
        - Safe for parallel execution
        - Thread-safe (no shared state)
    """
    # Handle None case
    if latest_commit_timestamp is None:
        return 0

    # Compute days elapsed
    time_delta = eval_now - latest_commit_timestamp
    days = floor(time_delta.total_seconds() / 86400)

    # Clamp days to non-negative (future commits treated as 0 days)
    days = max(0, days)

    # Scoring logic
    if days <= 0:
        return 100

    if days >= 90:
        return 0

    # Linear interpolation: 100 * (1 - days/90)
    score = 100 * (1 - days / 90)
    return round(score)
