# Copilot Instructions for zsh-uv-env

## Repository Summary

zsh-uv-env is a minimal zsh plugin that automatically activates and deactivates Python virtual environments (.venv directories) as you navigate through your filesystem. The plugin integrates with Oh My Zsh and provides a hook system for custom post-activation/deactivation commands.

## High-Level Repository Information

- **Repository Type**: Zsh shell plugin
- **Size**: Extremely small (4 files, 188 total lines)
- **Language**: Shell script (zsh syntax)
- **Target Runtime**: Zsh shell with Python
- **Dependencies**: 
  - Zsh shell with add-zsh-hook support
  - Python (for creating .venv directories)
  - No external package dependencies
- **License**: MIT

## Build and Validation Instructions

### Prerequisites
- Zsh shell installed
- Python 3 (for creating test virtual environments)

### Syntax Validation
**Always run syntax validation before making changes:**
```bash
bash -n zsh-uv-env.plugin.zsh
```
This command should exit with status 0 (no output) if syntax is correct.

### Testing the Plugin
Since there are no automated tests, validation requires manual testing:

1. **Create test environment:**
   ```bash
   mkdir -p /tmp/test_plugin
   cd /tmp/test_plugin
   python3 -m venv .venv
   ```

2. **Source the plugin in zsh:**
   ```bash
   zsh  # Start zsh if not already in it
   source /path/to/zsh-uv-env.plugin.zsh
   ```

3. **Test activation:** Navigate into the test directory - the virtual environment should activate automatically.

4. **Test deactivation:** Navigate out of the directory - the virtual environment should deactivate.

### Validation Steps
- **Syntax check**: Run `bash -n zsh-uv-env.plugin.zsh` (takes <1 second)
- **Manual testing**: Create .venv directory and test navigation (takes 2-3 minutes)
- **Hook testing**: If modifying hook functionality, test with sample post-hooks

### Common Issues and Workarounds
- The plugin uses zsh-specific syntax (`typeset -g`, `add-zsh-hook`) that won't work in bash
- Always test in actual zsh environment, not bash
- Plugin behavior depends on zsh's precmd hook system

## Project Layout and Architecture

### File Structure
```
zsh-uv-env/
├── .git/                          # Git repository
├── LICENSE                        # MIT license (21 lines)
├── README.md                      # Installation and usage docs (64 lines)
└── zsh-uv-env.plugin.zsh         # Main plugin file (103 lines)
```

### Main Plugin Architecture (`zsh-uv-env.plugin.zsh`)

**Core Functions:**
- `is_venv_active()` (lines 2-5): Checks if virtual environment is already active
- `find_venv()` (lines 8-34): Traverses up directory tree to find .venv directories
- `autoenv_chpwd()` (lines 69-94): Main logic for activation/deactivation on directory change

**Hook System:**
- `ZSH_UV_ACTIVATE_HOOKS[]` (line 40): Array storing activation hook functions
- `ZSH_UV_DEACTIVATE_HOOKS[]` (line 41): Array storing deactivation hook functions
- `zsh_uv_add_post_hook_on_activate()` (lines 44-46): Register activation hooks
- `zsh_uv_add_post_hook_on_deactivate()` (lines 48-50): Register deactivation hooks

**State Management:**
- `AUTOENV_ACTIVATED` (line 37): Global flag tracking if plugin activated the current venv

### Integration Points
- Uses `add-zsh-hook precmd autoenv_chpwd` (line 100) to monitor directory changes
- Integrates with Oh My Zsh plugin system via filename convention
- Sources virtual environment activation scripts at `$venv_path/bin/activate`

### Key Behavioral Logic
1. Plugin searches for .venv directories starting from current directory
2. Search stops at either `$HOME` or filesystem root
3. Only auto-activates if no virtual environment is manually active
4. Tracks activation state to avoid interfering with manual venv management
5. Runs user-defined hooks after activation/deactivation

### Configuration Files
- No configuration files exist
- All behavior is controlled through the main plugin file
- User customization happens via hook registration in `.zshrc`

### Dependencies and Requirements
- **Runtime Dependency**: Zsh with `add-zsh-hook` function (standard in modern zsh)
- **Usage Dependency**: Python for creating `.venv` directories
- **No package.json, requirements.txt, or other dependency files**

### Validation Pipeline
- No GitHub Actions or CI/CD configured
- No automated testing framework
- Validation relies on manual testing in zsh environment
- Consider adding basic shell syntax validation if implementing CI

### Making Changes
When modifying this plugin:
1. **Always** validate syntax first: `bash -n zsh-uv-env.plugin.zsh`
2. Test in actual zsh environment with real .venv directories
3. Consider impact on hook system if modifying activation/deactivation logic
4. Test edge cases: nested .venv directories, manual venv activation, home directory behavior
5. Verify the `AUTOENV_ACTIVATED` flag correctly tracks state changes

### README Contents Summary
The README provides:
- Installation instructions for Oh My Zsh users
- Basic usage explanation
- Hook system documentation with examples
- Function reference for `zsh_uv_add_post_hook_on_activate` and `zsh_uv_add_post_hook_on_deactivate`

### Trust These Instructions
These instructions are comprehensive and validated. Only search for additional information if you encounter specific errors or need details not covered here. The repository is intentionally minimal - resist adding complexity unless absolutely necessary for the task at hand.