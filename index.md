# File Index

- **ui.py**
  - Main window setup, widget creation, event bindings.
  - Entry point for the application.
  - Functions: `parse_geometry`, `toggle_window_size`, `dismiss_context_menu`

- **state_manager.py**
  - Manages UI state: `set_initial_state`, `on_close`, `save_current_state`
  - Handles loading/saving window position, colors, etc.

- **repo_manager.py**
  - Repo-related UI logic: `create_new_repo`, `select_new_folder`, `show_context_menu`
  - Manages repository creation and context menu.

- **color_manager.py**
  - Color/font handling: `start_color_drag`, `update_color`, `apply_color`
  - Controls UI color adjustments.

- **constants.py**
  - Stores `GLOBAL_DEFAULTS` for colors, font sizes, and other static values.
  - Rarely edited constants.

- **logic.py**
  - Core logic: `save_state`, `load_state`, `update_treeview`, `clear_entry`, `run_git_command`, `check_git_status`, `update_editor`, `on_treeview_select`, `run_in_xterm`, `get_gh_username`, `show_gh_auth_status`, `BranchSelectDialog`
  - General utility functions.

- **git_commands.py**
  - Git-specific commands: `git_init`, `gh_repo_create`, `git_push`, `git_branch`, `git_branch_delete`, `git_checkout`, `delete_repo`, `_get_valid_path`, `_run_command`
  - Executes Git operations via xterm.