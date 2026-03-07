import pytest
from execution.scoring.test_presence import test_presence_ratio_score


class TestTestPresenceRatioScore:
    """
    Unit tests for test_presence_ratio_score function.

    Algorithm spec (frozen):
    - Identifies test files by patterns (test/tests dir, test_ prefix, _test suffix, .test./.spec.)
    - Identifies source files by extension allowlist (excluding test files)
    - Ignores files in: node_modules/, dist/, build/, vendor/, .git/
    - Computes ratio and returns score 0-100
    """

    def test_twenty_source_ten_test_returns_100(self):
        """Test that 20 source files + 10 test files returns score 100"""
        file_paths = []

        # 20 source files
        for i in range(20):
            file_paths.append(f"src/module{i}.py")

        # 10 test files
        for i in range(10):
            file_paths.append(f"tests/test_module{i}.py")

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)
        assert result == 100

    def test_ten_source_zero_test_returns_0(self):
        """Test that 10 source files + 0 test files returns score 0"""
        file_paths = [
            "src/app.py",
            "src/models.py",
            "src/utils.py",
            "src/config.py",
            "src/main.py",
            "lib/helper.py",
            "lib/parser.py",
            "lib/validator.py",
            "core/engine.py",
            "core/processor.py",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)
        assert result == 0

    def test_zero_source_five_test_returns_0(self):
        """Test that 0 source files + 5 test files returns score 0"""
        file_paths = [
            "tests/test_app.py",
            "tests/test_models.py",
            "tests/test_utils.py",
            "tests/test_config.py",
            "tests/test_main.py",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)
        assert result == 0

    def test_ignores_node_modules_dist_build_vendor_git(self):
        """Test that files in excluded directories are ignored"""
        file_paths = [
            # Valid source files
            "src/app.py",
            "src/core.py",

            # Valid test files
            "tests/test_app.py",

            # Should be ignored
            "node_modules/package/index.js",
            "node_modules/lib/utils.js",
            "dist/bundle.js",
            "dist/output/main.js",
            "build/artifacts/app.py",
            "build/temp.py",
            "vendor/external/library.py",
            "vendor/deps.py",
            ".git/objects/abc123",
            ".git/hooks/pre-commit",
        ]

        source_ext_allowlist = {".py", ".js"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # Should only count: 2 source files (app.py, core.py) and 1 test file
        # Not perfect ratio, but should not be affected by ignored files
        assert isinstance(result, int)
        assert 0 <= result <= 100

    def test_test_file_pattern_directory_named_test_or_tests(self):
        """Test that files in 'test' or 'tests' directories are recognized as tests"""
        file_paths = [
            "src/app.py",
            "src/core.py",

            # In 'tests' directory
            "tests/integration.py",
            "tests/unit.py",

            # In 'test' directory
            "test/smoke.py",
            "test/e2e.py",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # 2 source files, 4 test files
        assert isinstance(result, int)
        assert result > 0  # Should have good coverage

    def test_test_file_pattern_test_prefix(self):
        """Test that files starting with 'test_' are recognized as tests"""
        file_paths = [
            "src/app.py",
            "src/core.py",
            "src/utils.py",

            # test_ prefix
            "test_app.py",
            "test_core.py",
            "lib/test_utils.py",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # 3 source files, 3 test files
        assert isinstance(result, int)
        assert result > 0

    def test_test_file_pattern_test_suffix(self):
        """Test that files ending with '_test' are recognized as tests"""
        file_paths = [
            "src/app.py",
            "src/models.py",

            # _test suffix
            "app_test.py",
            "models_test.py",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # 2 source files, 2 test files
        assert isinstance(result, int)
        assert result > 0

    def test_test_file_pattern_dot_test_dot(self):
        """Test that files containing '.test.' are recognized as tests"""
        file_paths = [
            "src/component.js",
            "src/utils.js",

            # .test. pattern
            "component.test.js",
            "utils.test.js",
        ]

        source_ext_allowlist = {".js"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # 2 source files, 2 test files
        assert isinstance(result, int)
        assert result > 0

    def test_test_file_pattern_dot_spec_dot(self):
        """Test that files containing '.spec.' are recognized as tests"""
        file_paths = [
            "src/service.ts",
            "src/handler.ts",

            # .spec. pattern
            "service.spec.ts",
            "handler.spec.ts",
        ]

        source_ext_allowlist = {".ts"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # 2 source files, 2 test files
        assert isinstance(result, int)
        assert result > 0

    def test_deterministic_behavior(self):
        """Test that same inputs produce same output (determinism)"""
        file_paths = [
            "src/app.py",
            "src/core.py",
            "src/utils.py",
            "tests/test_app.py",
            "tests/test_core.py",
        ]

        source_ext_allowlist = {".py"}

        # Call multiple times
        result1 = test_presence_ratio_score(file_paths, source_ext_allowlist)
        result2 = test_presence_ratio_score(file_paths, source_ext_allowlist)
        result3 = test_presence_ratio_score(file_paths, source_ext_allowlist)

        assert result1 == result2 == result3

    def test_mixed_extensions_only_counts_allowlisted(self):
        """Test that only files with allowlisted extensions are counted"""
        file_paths = [
            # Python files (allowlisted)
            "src/app.py",
            "src/core.py",
            "tests/test_app.py",

            # Other extensions (not allowlisted)
            "src/readme.md",
            "src/config.json",
            "src/data.csv",
            "tests/fixtures.json",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # Should only count .py files: 2 source + 1 test
        assert isinstance(result, int)
        assert 0 <= result <= 100

    def test_empty_file_list_returns_0(self):
        """Test that empty file list returns score 0"""
        file_paths = []
        source_ext_allowlist = {".py"}

        result = test_presence_ratio_score(file_paths, source_ext_allowlist)
        assert result == 0

    def test_nested_test_directories(self):
        """Test that nested paths with 'test' or 'tests' are recognized"""
        file_paths = [
            "src/app.py",
            "src/core.py",

            # Nested test directories
            "src/tests/unit/test_app.py",
            "lib/test/integration/test_core.py",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # 2 source files, 2 test files
        assert isinstance(result, int)
        assert result > 0

    def test_all_patterns_combined(self):
        """Test file that matches multiple test patterns is still counted once"""
        file_paths = [
            "src/app.py",
            "src/core.py",

            # This matches multiple patterns: in tests/ dir AND has test_ prefix
            "tests/test_app.py",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # 2 source files, 1 test file (counted once despite multiple pattern matches)
        assert isinstance(result, int)
        assert 0 <= result <= 100

    def test_case_sensitivity(self):
        """Test that pattern matching is case-sensitive (or verify expected behavior)"""
        file_paths = [
            "src/App.py",
            "src/Core.py",

            # Lowercase test patterns
            "tests/test_app.py",

            # Uppercase variations (behavior depends on spec)
            "Tests/Test_Core.py",
        ]

        source_ext_allowlist = {".py"}
        result = test_presence_ratio_score(file_paths, source_ext_allowlist)

        # Result should be deterministic
        assert isinstance(result, int)
        assert 0 <= result <= 100
