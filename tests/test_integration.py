# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
#!/usr/bin/env python3
"""
Integration tests for zsh-uv-env plugin

These tests create real directory structures with .venv directories
and test the full plugin behavior in realistic scenarios.
"""

import os
import tempfile
import subprocess
import time
from pathlib import Path


class IntegrationTester:
    """Integration test harness for end-to-end plugin behavior"""
    
    def __init__(self):
        self.plugin_path = Path(__file__).parent.parent / "zsh-uv-env.plugin.zsh"
        self.test_count = 0
        self.passed_count = 0
        
    def create_mock_venv(self, venv_path):
        """Create a mock .venv directory with activation script"""
        venv_path.mkdir(parents=True, exist_ok=True)
        bin_dir = venv_path / "bin"
        bin_dir.mkdir(exist_ok=True)
        
        # Create a mock activate script
        activate_script = bin_dir / "activate"
        activate_script.write_text(f"""
# Mock activate script for testing
export VIRTUAL_ENV="{venv_path}"
export PATH="{bin_dir}:$PATH"
echo "Mock venv activated: {venv_path}"

# Mock deactivate function
deactivate() {{
    unset VIRTUAL_ENV
    echo "Mock venv deactivated"
}}
""")
        activate_script.chmod(0o755)
    
    def run_zsh_test(self, commands, cwd=None):
        """Run a series of zsh commands and return the result"""
        # Build command string that sources plugin and runs commands
        # Reset environment state to ensure clean testing
        cmd_string = f"""
        # Reset environment state for clean testing
        unset VIRTUAL_ENV
        AUTOENV_ACTIVATED=0
        # Source the plugin
        source '{self.plugin_path}'
        {commands}
        """
        
        result = subprocess.run(
            ['zsh', '-c', cmd_string],
            capture_output=True,
            text=True,
            cwd=cwd,
            env={**os.environ, 'VIRTUAL_ENV': ''}  # Ensure VIRTUAL_ENV is not set
        )
        
        return result
    
    def assert_contains(self, expected, actual, test_name):
        """Assert that actual contains expected string"""
        self.test_count += 1
        if expected in actual:
            print(f"✓ {test_name}")
            self.passed_count += 1
        else:
            print(f"✗ {test_name}")
            print(f"  Expected to contain: {expected}")
            print(f"  Actual output: {actual}")
    
    def assert_not_contains(self, unexpected, actual, test_name):
        """Assert that actual does not contain unexpected string"""
        self.test_count += 1
        if unexpected not in actual:
            print(f"✓ {test_name}")
            self.passed_count += 1
        else:
            print(f"✗ {test_name}")
            print(f"  Should not contain: {unexpected}")
            print(f"  Actual output: {actual}")
    
    def test_basic_activation(self):
        """Test basic virtual environment activation"""
        print("\n=== Testing basic activation ===")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            venv_path = temp_path / ".venv"
            self.create_mock_venv(venv_path)
            
            # Test that autoenv_chpwd activates venv when entering directory
            result = self.run_zsh_test(f"""
            cd '{temp_path}'
            autoenv_chpwd
            echo "VIRTUAL_ENV=$VIRTUAL_ENV"
            echo "AUTOENV_ACTIVATED=$AUTOENV_ACTIVATED"
            """)
            
            self.assert_contains(f"VIRTUAL_ENV={venv_path}", result.stdout, 
                               "Virtual environment activated")
            self.assert_contains("AUTOENV_ACTIVATED=1", result.stdout,
                               "AUTOENV_ACTIVATED flag set")
    
    def test_deactivation_on_exit(self):
        """Test virtual environment deactivation when leaving directory"""
        print("\n=== Testing deactivation on exit ===")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            venv_path = temp_path / ".venv"
            self.create_mock_venv(venv_path)
            
            # Create a directory without .venv to navigate to
            import time
            other_dir = temp_path.parent / f"other_dir_{int(time.time() * 1000000)}" 
            other_dir.mkdir(exist_ok=True)
            
            result = self.run_zsh_test(f"""
            cd '{temp_path}'
            autoenv_chpwd  # Should activate
            cd '{other_dir}'
            autoenv_chpwd  # Should deactivate
            echo "VIRTUAL_ENV_AFTER=$VIRTUAL_ENV"
            echo "AUTOENV_ACTIVATED_AFTER=$AUTOENV_ACTIVATED"
            """)
            
            self.assert_contains("Mock venv deactivated", result.stdout,
                               "Virtual environment deactivated")
            self.assert_contains("AUTOENV_ACTIVATED_AFTER=0", result.stdout,
                               "AUTOENV_ACTIVATED flag reset")
    
    def test_nested_venv_search(self):
        """Test finding .venv in parent directories"""
        print("\n=== Testing nested .venv search ===")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            venv_path = temp_path / ".venv"
            self.create_mock_venv(venv_path)
            
            # Create nested subdirectory
            nested_dir = temp_path / "src" / "modules"
            nested_dir.mkdir(parents=True)
            
            result = self.run_zsh_test(f"""
            cd '{nested_dir}'
            autoenv_chpwd
            echo "VIRTUAL_ENV=$VIRTUAL_ENV"
            """)
            
            self.assert_contains(f"VIRTUAL_ENV={venv_path}", result.stdout,
                               "Found .venv in ancestor directory")
    
    def test_manual_venv_preservation(self):
        """Test that manually activated venvs are not interfered with"""
        print("\n=== Testing manual venv preservation ===")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            venv_path = temp_path / ".venv"
            self.create_mock_venv(venv_path)
            
            # Simulate manually activated venv
            result = self.run_zsh_test(f"""
            export VIRTUAL_ENV="/manual/venv/path"
            cd '{temp_path}'
            autoenv_chpwd
            echo "VIRTUAL_ENV=$VIRTUAL_ENV"
            echo "AUTOENV_ACTIVATED=$AUTOENV_ACTIVATED"
            """)
            
            self.assert_contains("VIRTUAL_ENV=/manual/venv/path", result.stdout,
                               "Manual venv preserved")
            self.assert_contains("AUTOENV_ACTIVATED=0", result.stdout,
                               "AUTOENV_ACTIVATED remains 0 for manual venv")
    
    def test_hook_integration(self):
        """Test that hooks are called during activation/deactivation"""
        print("\n=== Testing hook integration ===")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            venv_path = temp_path / ".venv"
            self.create_mock_venv(venv_path)
            
            # Create a unique directory name using timestamp to avoid collisions
            import time
            other_dir = temp_path.parent / f"other_dir_{int(time.time() * 1000000)}"
            other_dir.mkdir(exist_ok=True)
            
            result = self.run_zsh_test(f"""
            # Define test hooks
            activate_hook() {{ echo "ACTIVATE_HOOK_CALLED"; }}
            deactivate_hook() {{ echo "DEACTIVATE_HOOK_CALLED"; }}
            
            # Register hooks
            zsh_uv_add_post_hook_on_activate 'activate_hook'
            zsh_uv_add_post_hook_on_deactivate 'deactivate_hook'
            
            # Test activation
            cd '{temp_path}'
            autoenv_chpwd
            
            # Test deactivation
            cd '{other_dir}'
            autoenv_chpwd
            """)
            
            self.assert_contains("ACTIVATE_HOOK_CALLED", result.stdout,
                               "Activation hook called")
            self.assert_contains("DEACTIVATE_HOOK_CALLED", result.stdout,
                               "Deactivation hook called")
    
    def run_all_tests(self):
        """Run all integration test methods"""
        print("Running zsh-uv-env integration tests...")
        print(f"Plugin path: {self.plugin_path}")
        
        # Check prerequisites
        if not self.plugin_path.exists():
            print(f"ERROR: Plugin file not found at {self.plugin_path}")
            return False
        
        try:
            subprocess.run(['zsh', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: zsh not found. Please install zsh to run these tests.")
            return False
        
        # Run all test methods
        self.test_basic_activation()
        self.test_deactivation_on_exit()
        self.test_nested_venv_search()
        self.test_manual_venv_preservation()
        self.test_hook_integration()
        
        # Print summary
        print(f"\n=== Integration Test Summary ===")
        print(f"Total tests: {self.test_count}")
        print(f"Passed: {self.passed_count}")
        print(f"Failed: {self.test_count - self.passed_count}")
        
        if self.passed_count == self.test_count:
            print("✓ All integration tests passed!")
            return True
        else:
            print("✗ Some integration tests failed!")
            return False


if __name__ == "__main__":
    import sys
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)