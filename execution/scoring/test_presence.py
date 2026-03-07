__test__ = False


def test_presence_ratio_score(
    repo_file_paths: list[str],
    source_ext_allowlist: set[str]
) -> int:
    """
    Calculate a test coverage score (0-100) based on test-to-source file ratio.

    This is a pure, deterministic function with no I/O or side effects.

    Algorithm (frozen spec):
    - Identifies test files by patterns (test/tests dir, test_ prefix, _test suffix, .test./.spec.)
    - Identifies source files by extension allowlist (excluding test files)
    - Ignores files in: node_modules/, dist/, build/, vendor/, .git/
    - Computes ratio: r = T / S
    - Score = round(100 * min(r / 0.5, 1))

    Args:
        repo_file_paths: List of all file paths in the repository
        source_ext_allowlist: Set of file extensions to consider as source code (e.g., {".py", ".js"})

    Returns:
        int: Test presence score from 0-100, where:
            - 0 = no tests or no source files
            - 100 = optimal test-to-source ratio (0.5 = 1 test per 2 source files)
            - Linear scaling: score = 100 * min(ratio / 0.5, 1)

    Examples:
        >>> # 20 source files + 10 test files
        >>> files = [f"src/module{i}.py" for i in range(20)]
        >>> files += [f"tests/test_module{i}.py" for i in range(10)]
        >>> test_presence_ratio_score(files, {".py"})
        100

    Determinism:
        - No randomness, no I/O, no filesystem access
        - Same inputs always produce same output
        - Safe for parallel execution
        - Thread-safe (no shared state)
    """
    # Ignored path segments
    IGNORED_SEGMENTS = {'node_modules', 'dist', 'build', 'vendor', '.git'}

    def is_ignored(path: str) -> bool:
        """Check if file path contains any ignored segments."""
        # Normalize path separators to forward slashes
        normalized = path.replace('\\', '/')
        parts = normalized.split('/')
        return any(segment in IGNORED_SEGMENTS for segment in parts)

    def is_test_file(path: str) -> bool:
        """Check if file matches test file patterns."""
        # Normalize path separators
        normalized = path.replace('\\', '/')
        parts = normalized.split('/')

        # Check if any path segment is exactly "test" or "tests"
        if any(segment in {'test', 'tests'} for segment in parts):
            return True

        # Get basename (last part of path)
        basename = parts[-1] if parts else ''

        # Check if basename starts with "test_"
        if basename.startswith('test_'):
            return True

        # Check if basename (without extension) ends with "_test"
        # Extract name without extension
        name_without_ext = basename
        if '.' in basename:
            name_without_ext = basename.rsplit('.', 1)[0]
        if name_without_ext.endswith('_test'):
            return True

        # Check if basename contains ".test." or ".spec."
        if '.test.' in basename or '.spec.' in basename:
            return True

        return False

    def get_extension(path: str) -> str:
        """Extract file extension from path."""
        # Normalize path separators
        normalized = path.replace('\\', '/')
        basename = normalized.split('/')[-1]
        if '.' in basename:
            return '.' + basename.rsplit('.', 1)[1]
        return ''

    # Count source and test files
    source_files = 0
    test_files = 0

    for path in repo_file_paths:
        # Skip ignored files
        if is_ignored(path):
            continue

        # Check if it's a test file (test classification overrides source)
        if is_test_file(path):
            test_files += 1
            continue  # Don't count as source

        # Check if it's a source file (by extension)
        ext = get_extension(path)
        if ext in source_ext_allowlist:
            source_files += 1

    # Calculate score
    if source_files == 0:
        return 0

    ratio = test_files / source_files
    score = 100 * min(ratio / 0.5, 1)
    return round(score)


test_presence_ratio_score.__test__ = False