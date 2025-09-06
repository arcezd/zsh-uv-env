# Function to check if a virtualenv is already activated
# Returns 0 (success) if VIRTUAL_ENV environment variable is set, 1 otherwise
# This helps distinguish between manually activated venvs and auto-activated ones
is_venv_active() {
    [[ -n "$VIRTUAL_ENV" ]] && return 0
    return 1
}

# Function to find nearest .venv directory by traversing up the directory tree
# Searches from current directory upward until reaching home directory or filesystem root
# Returns the path to the .venv directory if found, or exits with status 1 if not found
# Logic: Stop at home directory if we're under it, otherwise stop at filesystem root
find_venv() {
    local current_dir="$PWD"
    local home_dir="$HOME"
    local root_dir="/"
    local stop_dir="$root_dir"

    # If we're under home directory, stop at home to avoid searching system directories
    if [[ "$current_dir" == "$home_dir"* ]]; then
        stop_dir="$home_dir"
    fi

    # Traverse up the directory tree looking for .venv
    while [[ "$current_dir" != "$stop_dir" ]]; do
        if [[ -d "$current_dir/.venv" ]]; then
            echo "$current_dir/.venv"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done

    # Check the stop directory itself (home or root)
    if [[ -d "$stop_dir/.venv" ]]; then
        echo "$stop_dir/.venv"
        return 0
    fi

    return 1
}

# Global flag to track if this plugin activated the current virtual environment
# 0 = not activated by plugin (manual activation or no venv active)
# 1 = activated by plugin (will be deactivated automatically when leaving directory)
# This prevents interference with manually activated virtual environments
typeset -g AUTOENV_ACTIVATED=0

# Global arrays to store user-defined hook functions
# These hooks allow users to run custom commands after venv activation/deactivation
typeset -ga ZSH_UV_ACTIVATE_HOOKS=()
typeset -ga ZSH_UV_DEACTIVATE_HOOKS=()

# Public API: Register a function to be called after virtual environment activation
# Usage: zsh_uv_add_post_hook_on_activate 'my_function_name'
# The function will be executed each time a venv is auto-activated by this plugin
zsh_uv_add_post_hook_on_activate() {
    ZSH_UV_ACTIVATE_HOOKS+=("$1")
}

# Public API: Register a function to be called after virtual environment deactivation  
# Usage: zsh_uv_add_post_hook_on_deactivate 'my_function_name'
# The function will be executed each time a venv is auto-deactivated by this plugin
zsh_uv_add_post_hook_on_deactivate() {
    ZSH_UV_DEACTIVATE_HOOKS+=("$1")
}

# Internal function to execute all registered activation hooks
# Called automatically after a virtual environment is activated
# Uses eval to execute function names stored in the hooks array
_run_activate_hooks() {
    local hook
    for hook in "${ZSH_UV_ACTIVATE_HOOKS[@]}"; do
        eval "$hook"
    done
}

# Internal function to execute all registered deactivation hooks  
# Called automatically after a virtual environment is deactivated
# Uses eval to execute function names stored in the hooks array
_run_deactivate_hooks() {
    local hook
    for hook in "${ZSH_UV_DEACTIVATE_HOOKS[@]}"; do
        eval "$hook"
    done
}

# Main function that handles automatic virtual environment activation/deactivation
# Called by zsh's precmd hook on every directory change and command execution
# Core logic:
# 1. Respect manually activated venvs (don't interfere if user activated manually)
# 2. Search for .venv directory in current path
# 3. Activate found venv if none is currently active  
# 4. Deactivate plugin-activated venv when no .venv found in current path
autoenv_chpwd() {
    # Don't interfere if a virtualenv is already manually activated
    # Only proceed if no venv is active OR we activated the current one
    if is_venv_active && [[ $AUTOENV_ACTIVATED == 0 ]]; then
        return
    fi

    # Search for .venv directory starting from current directory
    local venv_path=$(find_venv)

    if [[ -n "$venv_path" ]]; then
        # Found a .venv directory
        if ! is_venv_active; then
            # No venv currently active, so activate the found one
            source "$venv_path/bin/activate"
            AUTOENV_ACTIVATED=1
            # Execute user-defined activation hooks
            _run_activate_hooks
        fi
        # If venv is already active and we're in a .venv directory, do nothing
        # This handles the case where we move between directories with the same .venv
    else
        # No .venv directory found in current path
        if [[ $AUTOENV_ACTIVATED == 1 ]] && is_venv_active; then
            # We previously activated a venv, so deactivate it
            deactivate
            AUTOENV_ACTIVATED=0
            # Execute user-defined deactivation hooks
            _run_deactivate_hooks
        fi
        # If no venv is active or it was manually activated, do nothing
    fi
}

# Plugin initialization: Set up the automatic monitoring system
# Using precmd hook instead of chpwd because precmd catches more cases:
# - Directory changes (like chpwd)  
# - New .venv creation in current directory
# - .venv deletion in current directory
# Trade-off: precmd runs on every command (slightly more overhead) but catches all cases
autoload -U add-zsh-hook
add-zsh-hook precmd autoenv_chpwd

# Run the check once when the plugin is first loaded
# This activates any .venv in the current directory when shell starts
autoenv_chpwd
