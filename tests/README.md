# Testing Documentation for zsh-uv-env

This directory contains a comprehensive test suite for the zsh-uv-env plugin.

## Test Files

- **`test_plugin.py`** - Unit tests for individual plugin functions
- **`test_integration.py`** - Integration tests for end-to-end behavior  
- **`run_tests.py`** - Test runner that executes all tests

## Running Tests

### Quick Start

Run all tests with a single command:

```bash
uv run tests/run_tests.py
```

### Running Individual Test Suites

Run only unit tests:
```bash
uv run tests/test_plugin.py
```

Run only integration tests:
```bash
uv run tests/test_integration.py
```

### Prerequisites

- Ensure `uv` is installed and available in your PATH
- **Python 3.6+** (for test runner)
- **zsh shell** (the plugin being tested)
- **Unix-like environment** (Linux, macOS, WSL)

#### Installing zsh

On Ubuntu/Debian:
```bash
sudo apt-get install zsh
```

On macOS:
```bash
brew install zsh
```

## Test Strategy

### Why Python for Testing a Zsh Plugin?

We chose Python as our testing framework for several strategic reasons:

1. **Natural Fit**: The plugin manages Python virtual environments, making Python a natural choice for testing
2. **Environment Management**: Python excels at creating/destroying temporary directories and mock .venv structures
3. **Process Control**: Python's subprocess module provides excellent control over zsh execution and output capture
4. **Maintainability**: Python tests are more readable and maintainable than equivalent shell script tests
5. **Rich Assertions**: Better error reporting and test organization compared to pure shell testing

### Alternative Approaches Considered

We evaluated several testing approaches:

- **Pure Shell/Zsh Tests**: Would be "native" but difficult to organize and maintain
- **Bats Framework**: Good for shell testing but adds external dependency
- **Manual Testing**: Not scalable or repeatable
- **Python Approach** ✅: Best balance of functionality, maintainability, and ease of use

## Test Coverage

### Unit Tests (`test_plugin.py`)

Tests individual functions in isolation:

- ✅ `is_venv_active()` - Virtual environment detection
- ✅ `find_venv()` - Directory traversal and .venv discovery
- ✅ Hook registration functions
- ✅ Hook execution functions  
- ✅ Global state variables

### Integration Tests (`test_integration.py`)

Tests end-to-end plugin behavior:

- ✅ Basic virtual environment activation
- ✅ Automatic deactivation when leaving directories
- ✅ Nested directory .venv discovery
- ✅ Manual virtual environment preservation
- ✅ Hook system integration

## Test Architecture

### Mock Virtual Environments

The tests create lightweight mock .venv directories with minimal activation scripts that:
- Set `VIRTUAL_ENV` environment variable
- Provide a mock `deactivate` function
- Print identifiable output for test validation

### Subprocess Testing

Tests execute zsh commands using Python's subprocess module:
- Source the plugin file
- Execute specific functions or full scenarios  
- Capture stdout/stderr and exit codes
- Validate expected behavior

### Temporary Directories

All tests use temporary directories that are automatically cleaned up:
- No pollution of the test environment
- Safe parallel test execution
- Realistic directory structures

## Expected Output

When all tests pass, you should see:

```
============================================================
ZSH-UV-ENV PLUGIN TEST SUITE
============================================================

========================================
RUNNING UNIT TESTS
========================================
Running zsh-uv-env plugin tests...

=== Testing is_venv_active function ===
✓ is_venv_active returns 1 when no VIRTUAL_ENV set
✓ is_venv_active returns 0 when VIRTUAL_ENV is set
✓ is_venv_active returns 1 when VIRTUAL_ENV is empty

[... more test output ...]

=== Test Summary ===
Total tests: 15
Passed: 15
Failed: 0
✓ All tests passed!

========================================
RUNNING INTEGRATION TESTS
========================================
[... integration test output ...]

============================================================
OVERALL TEST SUMMARY
============================================================
Total tests run: 25
Passed: 25
Failed: 0

🎉 ALL TESTS PASSED! 🎉
The zsh-uv-env plugin is working correctly.
```

## Troubleshooting

### Common Issues

**"zsh not found" error**:
- Install zsh using your system package manager
- Ensure zsh is in your PATH

**Permission errors**:
- Ensure test files are executable: `chmod +x tests/*.py`

**Import errors**:
- Run tests from the repository root directory
- Ensure Python 3.6+ is installed

### Test Failures

If tests fail:
1. Check the detailed output to identify which specific test failed
2. Look at the "Expected vs Actual" output for unit tests
3. For integration tests, check if mock .venv directories are being created properly
4. Ensure the plugin file syntax is valid: `bash -n zsh-uv-env.plugin.zsh`

## Contributing

When adding new plugin features:
1. Add corresponding unit tests for new functions
2. Add integration tests for new end-to-end behavior
3. Update this documentation if needed
4. Ensure all tests pass before submitting changes

The test suite is designed to be comprehensive yet lightweight, providing confidence in plugin functionality without excessive complexity.