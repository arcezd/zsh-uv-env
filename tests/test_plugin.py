# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
#!/usr/bin/env python3
"""
Unit tests for zsh-uv-env plugin

This test suite validates the core functionality of the zsh-uv-env plugin
by testing individual functions in isolation using shell subprocess calls.
"""

import os
import tempfile
import subprocess
import shutil
import sys
from pathlib import Path


class PluginTester:
    """Test harness for zsh-uv-env plugin functionality"""
    
    def __init__(self):
        self.plugin_path = Path(__file__).parent.parent / "zsh-uv-env.plugin.zsh"
        self.test_count = 0
        self.passed_count = 0
        
    def run_zsh_function(self, function_call, env_vars=None):
        """Execute a zsh function from the plugin and return result"""
        # Source the plugin and call the function
        cmd = f"""
        source '{self.plugin_path}'
        {function_call}
        """
        
        result = subprocess.run(
            ['zsh', '-c', cmd],
            capture_output=True,
            text=True,
            env={**os.environ, **(env_vars or {})}
        )
        
        return result
    
    def assert_equals(self, expected, actual, test_name):
        """Simple assertion helper"""
        self.test_count += 1
        if expected == actual:
            print(f"✓ {test_name}")
            self.passed_count += 1
        else:
            print(f"✗ {test_name}")
            print(f"  Expected: {expected}")
            print(f"  Actual: {actual}")
    
    def assert_exit_code(self, expected_code, result, test_name):
        """Assert subprocess exit code"""
        self.assert_equals(expected_code, result.returncode, test_name)
    
    def test_is_venv_active(self):
        """Test is_venv_active function"""
        print("\n=== Testing is_venv_active function ===")
        
        # Test when no VIRTUAL_ENV is set (unset any existing VIRTUAL_ENV)
        result = self.run_zsh_function("unset VIRTUAL_ENV; is_venv_active")
        self.assert_exit_code(1, result, "is_venv_active returns 1 when no VIRTUAL_ENV set")
        
        # Test when VIRTUAL_ENV is set
        result = self.run_zsh_function(
            "is_venv_active", 
            env_vars={"VIRTUAL_ENV": "/some/venv/path"}
        )
        self.assert_exit_code(0, result, "is_venv_active returns 0 when VIRTUAL_ENV is set")
        
        # Test with empty VIRTUAL_ENV
        result = self.run_zsh_function(
            "is_venv_active",
            env_vars={"VIRTUAL_ENV": ""}
        )
        self.assert_exit_code(1, result, "is_venv_active returns 1 when VIRTUAL_ENV is empty")
    
    def test_find_venv(self):
        """Test find_venv function with various directory structures"""
        print("\n=== Testing find_venv function ===")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test: no .venv directory found
            result = self.run_zsh_function(f"cd '{temp_path}' && find_venv")
            self.assert_exit_code(1, result, "find_venv returns 1 when no .venv found")
            
            # Test: .venv in current directory
            venv_dir = temp_path / ".venv"
            venv_dir.mkdir()
            
            result = self.run_zsh_function(f"cd '{temp_path}' && find_venv")
            self.assert_exit_code(0, result, "find_venv returns 0 when .venv in current dir")
            self.assert_equals(str(venv_dir), result.stdout.strip(), "find_venv outputs correct path")
            
            # Test: .venv in parent directory
            subdir = temp_path / "subdir"
            subdir.mkdir()
            
            result = self.run_zsh_function(f"cd '{subdir}' && find_venv")
            self.assert_exit_code(0, result, "find_venv returns 0 when .venv in parent dir")
            self.assert_equals(str(venv_dir), result.stdout.strip(), "find_venv finds parent .venv")
            
            # Test: nested subdirectories
            deep_dir = subdir / "deep" / "nested"
            deep_dir.mkdir(parents=True)
            
            result = self.run_zsh_function(f"cd '{deep_dir}' && find_venv")
            self.assert_exit_code(0, result, "find_venv traverses multiple parent directories")
            self.assert_equals(str(venv_dir), result.stdout.strip(), "find_venv finds ancestor .venv")
    
    def test_hook_registration(self):
        """Test hook registration functions"""
        print("\n=== Testing hook registration ===")
        
        # Test activation hook registration
        result = self.run_zsh_function("""
        zsh_uv_add_post_hook_on_activate 'echo "activated"'
        echo ${#ZSH_UV_ACTIVATE_HOOKS[@]}
        """)
        self.assert_exit_code(0, result, "Activation hook registration succeeds")
        self.assert_equals("1", result.stdout.strip(), "One activation hook registered")
        
        # Test deactivation hook registration
        result = self.run_zsh_function("""
        zsh_uv_add_post_hook_on_deactivate 'echo "deactivated"'
        echo ${#ZSH_UV_DEACTIVATE_HOOKS[@]}
        """)
        self.assert_exit_code(0, result, "Deactivation hook registration succeeds")
        self.assert_equals("1", result.stdout.strip(), "One deactivation hook registered")
        
        # Test multiple hooks
        result = self.run_zsh_function("""
        zsh_uv_add_post_hook_on_activate 'hook1'
        zsh_uv_add_post_hook_on_activate 'hook2'
        echo ${#ZSH_UV_ACTIVATE_HOOKS[@]}
        """)
        self.assert_equals("2", result.stdout.strip(), "Multiple activation hooks registered")
    
    def test_hook_execution(self):
        """Test that hooks are executed properly"""
        print("\n=== Testing hook execution ===")
        
        # Test activation hook execution
        result = self.run_zsh_function("""
        test_hook() { echo "hook executed"; }
        zsh_uv_add_post_hook_on_activate 'test_hook'
        _run_activate_hooks
        """)
        self.assert_exit_code(0, result, "Activation hooks execute without error")
        self.assert_equals("hook executed", result.stdout.strip(), "Activation hook produces expected output")
        
        # Test deactivation hook execution  
        result = self.run_zsh_function("""
        test_deactivate_hook() { echo "deactivate hook executed"; }
        zsh_uv_add_post_hook_on_deactivate 'test_deactivate_hook'
        _run_deactivate_hooks
        """)
        self.assert_exit_code(0, result, "Deactivation hooks execute without error")
        self.assert_equals("deactivate hook executed", result.stdout.strip(), "Deactivation hook produces expected output")
    
    def test_autoenv_activated_flag(self):
        """Test AUTOENV_ACTIVATED flag behavior"""
        print("\n=== Testing AUTOENV_ACTIVATED flag ===")
        
        # Test initial state
        result = self.run_zsh_function("echo $AUTOENV_ACTIVATED")
        self.assert_equals("0", result.stdout.strip(), "AUTOENV_ACTIVATED starts at 0")
        
        # Test setting flag
        result = self.run_zsh_function("""
        AUTOENV_ACTIVATED=1
        echo $AUTOENV_ACTIVATED
        """)
        self.assert_equals("1", result.stdout.strip(), "AUTOENV_ACTIVATED can be set to 1")
    
    def run_all_tests(self):
        """Run all test methods"""
        print("Running zsh-uv-env plugin tests...")
        print(f"Plugin path: {self.plugin_path}")
        
        # Check if plugin file exists
        if not self.plugin_path.exists():
            print(f"ERROR: Plugin file not found at {self.plugin_path}")
            return False
        
        # Check if zsh is available
        try:
            subprocess.run(['zsh', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: zsh not found. Please install zsh to run these tests.")
            return False
        
        # Run all test methods
        self.test_is_venv_active()
        self.test_find_venv()
        self.test_hook_registration()
        self.test_hook_execution()
        self.test_autoenv_activated_flag()
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {self.test_count}")
        print(f"Passed: {self.passed_count}")
        print(f"Failed: {self.test_count - self.passed_count}")
        
        if self.passed_count == self.test_count:
            print("✓ All tests passed!")
            return True
        else:
            print("✗ Some tests failed!")
            return False


if __name__ == "__main__":
    tester = PluginTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)