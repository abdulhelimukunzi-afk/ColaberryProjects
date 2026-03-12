def release_tag_regularity_score(tag_names: list[str]) -> int:
    """
    Calculate a release regularity score (0-100) based on number of release tags.

    This is a pure, deterministic function with no I/O or side effects.

    Algorithm (frozen spec):
    - 0 tags       → 0
    - 1–2 tags     → 30
    - 3–5 tags     → 60
    - 6+ tags      → 100

    Args:
        tag_names: List of release tag name strings (e.g., ["v1.0.0", "v1.1.0"])

    Returns:
        int: Regularity score from 0-100, where:
            - 0   = no releases
            - 30  = minimal release history (1–2 tags)
            - 60  = moderate release cadence (3–5 tags)
            - 100 = mature release cadence (6+ tags)

    Determinism:
        - No randomness, no I/O, no system calls
        - Same inputs always produce same output
        - Tag name content is irrelevant; only count matters
    """
    count = len(tag_names)
    if count == 0:
        return 0
    if count <= 2:
        return 30
    if count <= 5:
        return 60
    return 100
