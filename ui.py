


import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from state_manager import set_initial_state, on_close
from color_manager import start_color_drag, update_color
from constants import *
from logic import *
from repo_manager import *

def show_context_menu(event, globals_dict):
    selection = globals_dict['treeview'].identify_row(event.y)
    if not selection:
        return
    
    globals_dict['treeview'].selection_set(selection)
    selected_item = globals_dict['treeview'].item(selection)["values"][0]  # Use values[0] instead of text
    base_path = globals_dict['entry'].get().strip()
    full_path = os.path.join(base_path, selected_item)
    
    # Load repo status to determine visibility
    from logic import load_repo_status, update_treeview
    repo_status = load_repo_status()
    is_private = repo_status.get(full_path, False)

    globals_dict['context_menu'] = tk.Menu(globals_dict['root'], tearoff=0)
    globals_dict['context_menu'].add_separator()
    globals_dict['context_menu'].add_command(label=f"     {selected_item}     ", font=("Helvetica", 11, "bold"), foreground="red", command=lambda: None)  # Bold simulation
    globals_dict['context_menu'].add_separator()
    globals_dict['context_menu'].add_command(label="Branch 2 New Repo", command=lambda: branch_to_new_repo(base_path, selected_item, full_path, globals_dict))
    globals_dict['context_menu'].add_separator()
    globals_dict['context_menu'].add_command(label=".Zip Branch", command=lambda: zip_from_branch(base_path, selected_item, full_path, globals_dict))
    globals_dict['context_menu'].add_command(label="Repo Link", command=lambda: copy_repo_link(globals_dict, selected_item))
    globals_dict['context_menu'].add_separator()
    globals_dict['context_menu'].add_command(label="Open Directory", command=lambda: open_directory(full_path))
    globals_dict['context_menu'].add_command(label="Claude Code", command=lambda: run_claude_code(full_path, base_path))
    globals_dict['context_menu'].add_separator()
    globals_dict['context_menu'].add_command(label="🌍 GO PUBLIC", command=lambda: go_public(globals_dict, selected_item, full_path))
    globals_dict['context_menu'].add_command(label="🔒 GO PRIVATE", command=lambda: go_private(globals_dict, selected_item, full_path))
    globals_dict['context_menu'].add_separator()
    globals_dict['context_menu'].add_command(label="RENAME", command=lambda: rename_repo(globals_dict, selected_item, base_path, full_path))
    globals_dict['context_menu'].add_command(label="DELETE", command=lambda: confirm_delete(globals_dict, selected_item))
    globals_dict['context_menu'].add_separator()

    globals_dict['context_menu'].post(event.x_root, event.y_root)
    globals_dict['menu_visible'] = True
    
def dismiss_context_menu(event, globals_dict):
    if globals_dict.get('menu_visible', False) and not (
        treeview.winfo_rootx() <= event.x_root <= treeview.winfo_rootx() + treeview.winfo_width() and
        treeview.winfo_rooty() <= event.y_root <= treeview.winfo_rooty() + treeview.winfo_height()
    ):
        globals_dict['context_menu'].unpost()
        globals_dict['menu_visible'] = False

def parse_geometry(geometry):
    width, rest = geometry.split('x')
    height, x, y = rest.split('+')
    return int(width), int(height), int(x), int(y)

def toggle_window_size():
    if not globals_dict['is_toggled']:
        globals_dict['normal_geometry'] = root.geometry()
        root.geometry(TOGGLE_GEOMETRY)
        globals_dict['is_toggled'] = True
    else:
        w, h, x, y = parse_geometry(globals_dict['normal_geometry'] if globals_dict['is_toggled'] else root.geometry())
        root.geometry(f"{w}x{h}+{x}+{y}")
        globals_dict['is_toggled'] = False

root = tk.Tk()
root.title("Code Cup ☕")
root.geometry("600x400")

main_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg='gray')
main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

left_frame = tk.Frame(main_paned, bg='white')
main_paned.add(left_frame, minsize=50)

entry_frame = tk.Frame(left_frame, bg='white')
entry_frame.pack(fill=tk.X, padx=2, pady=(2, 2))

clear_button = tk.Button(entry_frame, text="Cl", width=2, command=toggle_window_size)
clear_button.pack(side=tk.LEFT, padx=(0, 2))

entry = tk.Entry(entry_frame, font=("Courier", 10))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry.bind("<Return>", lambda e: update_treeview(entry, treeview))

treeview = ttk.Treeview(left_frame, show="tree", selectmode="browse", style="Custom.Treeview")
treeview.pack(fill=tk.BOTH, expand=True, padx=2, pady=(10, 0))  # 10 adds gap at top

# Add button container frame at the bottom of left_frame
bottom_button_frame = tk.Frame(left_frame, bg='white')
bottom_button_frame.pack(fill=tk.X, padx=2, pady=(2, 2))

# Row with two buttons (50% width each)
top_row_frame = tk.Frame(bottom_button_frame)
top_row_frame.pack(fill=tk.X)
tk.Button(top_row_frame, text="Clone", command=lambda: CloneDialog(root, "Clone Repository", globals_dict)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=0, pady=0)
tk.Button(top_row_frame, text="re4f.xyz").pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=0, pady=0)

# Logout/Login button (100% width)
def update_auth_button():
    from logic import get_gh_username
    username = get_gh_username()
    if username:
        auth_button.config(text="Logout", command=lambda: logout_gh())
    else:
        auth_button.config(text="Login", command=lambda: login_gh())

def logout_gh():
    from logic import run_in_xterm
    # Run the logout command
    subprocess.run("gh auth logout", shell=True, cwd=os.getcwd())
    # run_in_xterm("gh auth logout", os.getcwd())
    # Immediately update UI to logged-out state
    auth_button.config(text="Login", command=lambda: login_gh())
    current_branch = on_treeview_select(globals_dict['entry'], globals_dict['treeview'], 
                                       globals_dict['text_editor'], globals_dict['auth_label'])
    globals_dict['auth_label'].config(text=f"● {current_branch or 'No branch'} - You Are Not Logged In𝕏❌", fg="#FF0000")

def login_gh():
    from logic import show_gh_auth_status
    from tkinter import messagebox, Toplevel, Button, Label
    import subprocess

    # Run gh auth login in a visible xterm window
    full_command = f"xterm -e \"cd {os.getcwd()} && gh auth login && echo 'Press any key to close' && read -n 1\""
    process = subprocess.Popen(full_command, shell=True)

    # Custom dialog for login confirmation
    def check_login_status():
        dialog = Toplevel(globals_dict['root'])
        dialog.title("Login Confirmation")
        dialog.geometry("300x100")
        Label(dialog, text="Complete login in the terminal, then press Ok").pack(pady=20)
        ok_button = Button(dialog, text="Ok", command=lambda: post_login_check(dialog))
        ok_button.pack(side="left", padx=20)
        exit_button = Button(dialog, text="Exit", command=dialog.destroy)
        exit_button.pack(side="right", padx=20)
        dialog.transient(globals_dict['root'])
        dialog.grab_set()
        dialog.wait_window()

    def post_login_check(prev_dialog):
        prev_dialog.destroy()
        auth_status = show_gh_auth_status()
        if "Logged in to github.com" in auth_status:
            # Update UI immediately if logged in
            update_auth_button()
            current_branch = on_treeview_select(globals_dict['entry'], globals_dict['treeview'], 
                                              globals_dict['text_editor'], globals_dict['auth_label'])
            globals_dict['auth_label'].config(text=f"● {current_branch or 'No branch'} - {auth_status}")
        else:
            # Show retry prompt if not logged in
            retry_dialog = Toplevel(globals_dict['root'])
            retry_dialog.title("Login Check")
            retry_dialog.geometry("300x100")
            Label(retry_dialog, text="Login failed or incomplete; Press Ok to check again").pack(pady=20)
            ok_button = Button(retry_dialog, text="Ok", command=lambda: post_login_check(retry_dialog))
            exit_button = Button(retry_dialog, text="Exit", command=retry_dialog.destroy)
            ok_button.pack(side="left", padx=20)
            exit_button.pack(side="right", padx=20)
            retry_dialog.transient(globals_dict['root'])
            retry_dialog.grab_set()
            retry_dialog.wait_window()

    # Wait briefly before showing the dialog to ensure the xterm window appears first
    globals_dict['root'].after(500, check_login_status)

auth_button = tk.Button(left_frame, text="Checking...", command=lambda: None)
auth_button.pack(fill=tk.X, padx=1, pady=1)

treeview.bind("<<TreeviewSelect>>", lambda e: on_treeview_select(entry, treeview, text_editor, auth_label, update_auth=False))
treeview.bind("<Button-3>", lambda e: show_context_menu(e, globals_dict))
root.bind("<Button-3>", lambda e: dismiss_context_menu(e, globals_dict))
root.bind("<Button-1>", lambda e: dismiss_context_menu(e, globals_dict))

right_frame = tk.Frame(main_paned, bg='white')
main_paned.add(right_frame, minsize=50, stretch="always")

button_frame = tk.Frame(right_frame, bg='white')
button_frame.pack(fill=tk.X, pady=(0, 2))

for text, cmd in [
    ("New Repo", lambda: create_new_repo(globals_dict)),
    ("Save Branch", lambda: git_push(entry, treeview, globals_dict)),
    ("Swap Branch", lambda: git_checkout(entry, treeview, globals_dict, root)),
    ("New Branch", lambda: git_branch(entry, treeview, globals_dict)),
    ("Drop Branch", lambda: git_branch_delete(entry, treeview, globals_dict, root))
]:
    tk.Button(button_frame, text=text, command=cmd).pack(side=tk.LEFT, padx=2)

color_button = tk.Button(button_frame, text='🎨', width=2, font=("Arial", 18), padx=0, pady=0, borderwidth=0, highlightthickness=0)
color_button.pack(side=tk.LEFT, padx=2)
tk.Button(button_frame, text="Fetch Branch", command=lambda: git_rollback(entry, treeview, globals_dict)).pack(side=tk.LEFT, padx=2)

auth_label = tk.Label(right_frame, text="Checking GitHub auth...", bg='white', wraplength=0)
auth_label.pack(fill=tk.X, pady=(0, 2))

editor_frame = tk.Frame(right_frame, bg='white')
editor_frame.pack(fill=tk.BOTH, expand=True)  # No pady here to avoid extra spacing

text_editor = tk.Text(editor_frame, wrap=tk.NONE, font=("Courier", 10))
text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Side LEFT to place scrollbar on right

globals_dict = GLOBAL_DEFAULTS.copy()
globals_dict.update({'root': root, 'main_paned': main_paned, 'left_frame': left_frame, 'entry_frame': entry_frame,
                     'entry': entry, 'treeview': treeview, 'right_frame': right_frame, 'button_frame': button_frame,
                     'editor_frame': editor_frame, 'text_editor': text_editor, 'auth_label': auth_label, 'menu_visible': False})

style = ttk.Style()
style.configure("Custom.Treeview", font=("Courier", 12), rowheight=25, padding=[0, 0, 0, 0])
globals_dict['style'] = style

color_events = {
    '<Button-1>': lambda e: None,  # Block single left-click drag
    '<Button-3>': lambda e: None,  # Block single right-click drag
    '<Button-2>': lambda e: start_color_drag(e, 'frame_bg', globals_dict),
    '<B1-Motion>': lambda e: None,  # Block left motion
    '<B3-Motion>': lambda e: None,  # Block right motion
    '<B2-Motion>': lambda e: update_color(e, text_editor, entry, treeview, style, globals_dict),
    '<ButtonRelease-1>': lambda e: None,
    '<ButtonRelease-3>': lambda e: None,
}
for event, func in color_events.items():
    color_button.bind(event, func)

# Initial auth check after UI is set up
globals_dict['root'].after(100, update_auth_button)

root.deiconify()  # Show the window immediately

# Schedule state initialization and repo status regeneration after UI is visible
root.after(50, lambda: set_initial_state(globals_dict))
from logic import regenerate_repo_status
root.after(100, lambda: regenerate_repo_status(globals_dict['entry'], globals_dict['treeview'], globals_dict['root']))
root.protocol("WM_DELETE_WINDOW", lambda: on_close(globals_dict))
root.mainloop()