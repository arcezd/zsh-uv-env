# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
#!/usr/bin/env python3
"""
Test runner for zsh-uv-env plugin tests

This script runs both unit tests and integration tests and provides
a unified test report.
"""

import sys
import os
from pathlib import Path

# Add tests directory to path so we can import test modules
sys.path.insert(0, str(Path(__file__).parent))

from test_plugin import PluginTester
from test_integration import IntegrationTester


def main():
    """Run all tests and provide summary"""
    print("=" * 60)
    print("ZSH-UV-ENV PLUGIN TEST SUITE")
    print("=" * 60)
    
    # Check if we can run tests
    try:
        import subprocess
        subprocess.run(['zsh', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: zsh not found. Please install zsh to run these tests.")
        print("\nOn Ubuntu/Debian: sudo apt-get install zsh")
        print("On macOS: brew install zsh")
        print("On other systems: consult your package manager")
        return 1
    
    # Run unit tests
    print("\n" + "=" * 40)
    print("RUNNING UNIT TESTS")
    print("=" * 40)
    
    unit_tester = PluginTester()
    unit_success = unit_tester.run_all_tests()
    
    # Run integration tests
    print("\n" + "=" * 40)
    print("RUNNING INTEGRATION TESTS")
    print("=" * 40)
    
    integration_tester = IntegrationTester()
    integration_success = integration_tester.run_all_tests()
    
    # Overall summary
    print("\n" + "=" * 60)
    print("OVERALL TEST SUMMARY")
    print("=" * 60)
    
    total_tests = unit_tester.test_count + integration_tester.test_count
    total_passed = unit_tester.passed_count + integration_tester.passed_count
    total_failed = total_tests - total_passed
    
    print(f"Total tests run: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    
    if unit_success and integration_success:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The zsh-uv-env plugin is working correctly.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        if not unit_success:
            print("- Unit tests failed")
        if not integration_success:
            print("- Integration tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())