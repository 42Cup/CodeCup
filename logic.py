import json
import os
import subprocess
from tkinter import messagebox, simpledialog, ttk
import tkinter as tk

STATE_FILE = "ui_state.json"

def center_window_on_parent(window, parent):
    """
    Centers a window on its parent window.
    """
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    x = parent_x + (parent_width - width) // 2
    y = parent_y + (parent_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

class CenteredDialog(simpledialog.Dialog):
    """
    Base Dialog class that centers itself on the parent window.
    """
    def __init__(self, parent, title):
        self.parent = parent
        super().__init__(parent, title)
    
    def _set_transient(self, master=None):
        """
        Override the _set_transient method to center the dialog after it's created.
        This is called by the Dialog class after creating the window.
        """
        if master is None:
            master = self.parent
        super()._set_transient(master)
        
        # Center on parent after the dialog is fully created and sized
        self.update_idletasks()
        center_window_on_parent(self, master)

class AskString(CenteredDialog):
    """
    Replacement for simpledialog.askstring that centers on parent window.
    """
    def __init__(self, parent, title, prompt, initialvalue=None):
        self.prompt = prompt
        self.initialvalue = initialvalue
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt).pack(padx=10, pady=5)
        self.entry = tk.Entry(master, width=30)
        if self.initialvalue:
            self.entry.insert(0, self.initialvalue)
        self.entry.pack(padx=10, pady=5)
        self.entry.select_range(0, tk.END)
        return self.entry

    def apply(self):
        self.result = self.entry.get()
        
    def buttonbox(self):
        box = tk.Frame(self)
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

def centered_askstring(parent, title, prompt, initialvalue=None):
    """
    A version of askstring that centers the dialog on the parent window.
    """
    dialog = AskString(parent, title, prompt, initialvalue)
    return dialog.result

class AskYesNo(CenteredDialog):
    """
    Replacement for messagebox.askyesno that centers on parent window.
    """
    def __init__(self, parent, title, message):
        self.message = message
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.message, wraplength=300, justify="left").pack(padx=10, pady=10)
        return None

    def buttonbox(self):
        box = tk.Frame(self)
        yes_button = tk.Button(box, text="Yes", command=self.yes, width=10)
        yes_button.pack(side=tk.LEFT, padx=5, pady=5)
        no_button = tk.Button(box, text="No", command=self.no, width=10, default=tk.ACTIVE)
        no_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.yes)
        self.bind("<Escape>", self.no)
        box.pack()

    def yes(self, event=None):
        self.result = True
        self.destroy()

    def no(self, event=None):
        self.result = False
        self.destroy()

def centered_askyesno(parent, title, message):
    """
    A version of askyesno that centers the dialog on the parent window.
    """
    dialog = AskYesNo(parent, title, message)
    return dialog.result

def save_state(sash_pos, url, width, height, x, y, font_color, list_bg_color, frame_bg_color, list_item_bg_color, font_size):
    with open(STATE_FILE, 'w') as f:
        json.dump({
            "sash_position": sash_pos, "url": url, "width": width, "height": height, "x": x, "y": y,
            "font_color": font_color, "list_bg_color": list_bg_color, "frame_bg_color": frame_bg_color,
            "list_item_bg_color": list_item_bg_color, "font_size": font_size
        }, f)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try:
                state = json.load(f)
                return (
                    state.get("sash_position", 200), state.get("url", ""), state.get("width", 600), state.get("height", 400),
                    state.get("x", None), state.get("y", None), state.get("font_color", "#000000"),
                    state.get("list_bg_color", "#f0f0f0"), state.get("frame_bg_color", "#ffffff"),
                    state.get("list_item_bg_color", "#ffffff"), state.get("font_size", 10)
                )
            except json.JSONDecodeError:
                return 200, "", 600, 400, None, None, "#000000", "#f0f0f0", "#ffffff", "#ffffff", 10
    return 200, "", 600, 400, None, None, "#000000", "#f0f0f0", "#ffffff", "#ffffff", 10

# UPDATE TREEVIEW CLEARS ALL SELECTIONS WHEN REFRESHING LIST
def update_treeview(entry, treeview, event=None):
    path = entry.get().strip()
    treeview.delete(*treeview.get_children())
    if not os.path.isdir(path):
        treeview.insert("", "end", text="Invalid directory path")
        return
    
    try:
        items = sorted([item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))])
        repo_status = load_repo_status()
        for item in items:
            if os.path.isdir(os.path.join(path, item, ".git")):
                full_path = os.path.join(path, item)
                prefix = "🔒 " if repo_status.get(full_path, False) else "🌍 "
                treeview.insert("", "end", text=f"{prefix}{item}", values=(item,))
    except OSError:
        treeview.insert("", "end", text="Error accessing directory")

def clear_entry(entry, treeview):
    entry.delete(0, 'end')
    treeview.delete(*treeview.get_children())

# DATA RETRIEVAL ONLY
def run_git_command(command, cwd, default_output=""):
    try:
        return subprocess.check_output(command, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e:
        return default_output if not e.output else e.output

def check_git_status(full_path):
    status_output = run_git_command(["git", "status"], full_path)
    return "nothing to commit, working tree clean" in status_output

def update_editor(text_editor, lines):
    text_editor.delete(1.0, 'end')
    text_editor.tag_configure("bold_large", font=("TkDefaultFont", 12, "bold"))
    text_editor.tag_configure("bold_medium", font=("TkDefaultFont", 10, "bold"))
    text_editor.tag_configure("bold_larger", font=("TkDefaultFont", 14, "bold"))
    text_editor.tag_configure("normal", font=("TkDefaultFont", 9))
    for line in lines:
        if isinstance(line, tuple):
            text, tag = line
            text_editor.insert('end', f"{text}\n", tag)
        else:
            text_editor.insert('end', f"{line}\n", "normal")

# SIMULATE TREEVIEW / LEFT PANEL CLICK (Updates Right Panel Git Status View)
def on_treeview_select(entry, treeview, text_editor, auth_label, event=None, update_auth=True):
    selection = treeview.selection()
    if not selection or not os.path.isdir(entry.get().strip()):
        update_editor(text_editor, ["No folder selected" if not selection else "Invalid or non-Git directory"])
        return None

    item_values = treeview.item(selection[0])["values"]
    if not item_values or not os.path.isdir(os.path.join(entry.get().strip(), item_values[0], ".git")):
        update_editor(text_editor, ["Invalid or non-Git directory"])
        return None

    full_path = os.path.join(entry.get().strip(), item_values[0])
    commit_exists = run_git_command(["git", "log", "-1"], full_path, "").strip() != ""
    status_raw = run_git_command(["git", "status"], full_path, "No commits yet") if commit_exists else "No commits yet"
    status_lines = status_raw.splitlines()
    status_formatted = [f"**Status: {status_lines[0]}**", ""] + [
        f"  {line}" if "Changes not staged" in line else f"    {line}"
        for line in status_lines[1:] if line.strip()
    ]
    log = run_git_command(["git", "log", "-1", "--pretty=format:%h - %s (%an, %ar)"], full_path, "No commits") if commit_exists else "No commits"
    branches = run_git_command(["git", "branch"], full_path, "").splitlines() if commit_exists else []
    current_branch = "main" if not commit_exists else next((s.split()[-1] for s in status_raw.splitlines() if s.startswith("On branch")), "unknown")

    text_editor.tag_configure("bold_larger", font=("TkDefaultFont", 14, "bold"))
    update_editor(text_editor, [
        (f"Git repo at: {full_path}", "bold_large"),
        ("", "normal"),
        (status_formatted[0].replace("**", ""), "bold_medium")
    ] + [(line, "normal") for line in status_formatted[1:]] + [
        ("", "normal"),
        (f"Branch: {current_branch}", "bold_larger"),
        ("", "normal"),
        (f"Last Commit: {log}", "bold_medium"),
        ("", "normal"),
        ("Branches:", "bold_medium")
    ] + [(branch, "normal") for branch in branches])
    
    current_text = auth_label.cget('text')
    circle_color = "#008000" if "Changes not staged for commit:" not in status_raw else "#FF0000"
    auth_label.config(text=f"● {current_branch} {'(no commits)' * (not commit_exists)} - {current_text.split(' - ')[1]}", fg=circle_color)
    return current_branch

def run_in_xterm(command, cwd):
    full_command = f"cd {cwd} && ({command} || echo \"Command failed\")"
    subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def run_in_xterm_zip(command, cwd, headless=True):
    full_command = f"cd {cwd} && {command}" if headless else f"xterm -e \"cd {cwd} && {command} && echo 'Press any key to close' && read -n 1\""
    subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE if headless else None)

def select_new_folder(globals_dict, folder_name):
    for item in globals_dict['treeview'].get_children():
        if globals_dict['treeview'].item(item)["values"][0] == folder_name:
            globals_dict['treeview'].selection_set(item)
            globals_dict['treeview'].focus(item)
            current_branch = on_treeview_select(globals_dict['entry'], globals_dict['treeview'], 
                                              globals_dict['text_editor'], globals_dict['auth_label'])
            auth_status = globals_dict['auth_label'].cget("text").split(" - ")[1]
            globals_dict['auth_label'].config(text=f"● {current_branch if current_branch else 'No branch'} - {auth_status}", fg="#000000")
            break

def confirm_and_run_command(full_command, cwd, globals_dict, new_repo_name=None, prompt_message=""):
    HEADLESS = True
    formatted_command = full_command.replace('&&', '\n\n')
    
    class ConfirmDialog(CenteredDialog):
        def __init__(self, parent, title, message):
            self.message = message
            self.result = None
            super().__init__(parent, title)
        
        def body(self, master):
            WIDTH_MULTIPLIER, MAX_WIDTH = 2, 375
            BASE_WIDTH, WRAPLENGTH_OFFSET = 200, 25
            FONT_SIZE = 10
            
            longest_line = max(self.message.splitlines(), key=len, default="")
            width = min(BASE_WIDTH + (len(longest_line) * WIDTH_MULTIPLIER), MAX_WIDTH)
            
            label = tk.Label(master, text=self.message, font=("TkDefaultFont", FONT_SIZE, "bold"), 
                           wraplength=width-WRAPLENGTH_OFFSET, justify="left")
            label.pack(padx=10, pady=10)
            return label
        
        def buttonbox(self):
            box = tk.Frame(self)
            yes_button = tk.Button(box, text="Yes", command=self.yes, width=10)
            yes_button.pack(side=tk.LEFT, padx=5, pady=5)
            no_button = tk.Button(box, text="No", command=self.no, width=10, default=tk.ACTIVE)
            no_button.pack(side=tk.LEFT, padx=5, pady=5)
            self.bind("<Return>", self.yes)
            self.bind("<Escape>", self.no)
            box.pack()
        
        def yes(self, event=None):
            self.result = True
            self.destroy()
        
        def no(self, event=None):
            self.result = False
            self.destroy()

    dialog = ConfirmDialog(globals_dict['root'], "RUN COMMANDS", formatted_command)
    if not dialog.result:
        return False
        
    if HEADLESS:
        subprocess.run(full_command, cwd=cwd, shell=True, check=True)
    else:
        run_in_xterm(full_command, cwd)
    
    if new_repo_name:
        globals_dict['root'].after(1000, lambda: [
            update_repo_status(globals_dict['entry'], globals_dict['treeview']),
            select_new_folder(globals_dict, new_repo_name)
        ])
    globals_dict['root'].after(1000, lambda: on_treeview_select(
        globals_dict['entry'], globals_dict['treeview'], globals_dict['text_editor'], globals_dict['auth_label']
    ))
    return True

def get_gh_username():
    auth_output = run_git_command(["gh", "auth", "status"], None, "")
    for line in auth_output.splitlines():
        if "Logged in to github.com as" in line:
            return line.split("as")[1].split()[0].strip()
    return ""

def require_gh_login():
    username = get_gh_username()
    if not username:
        messagebox.showerror("Authentication Required", "You must be logged in to GitHub to perform this action.")
        return False
    return True

def show_gh_auth_status(text_editor=None):
    auth_output = run_git_command(["gh", "auth", "status"], None, "Error checking GitHub auth status")
    if text_editor:
        update_editor(text_editor, ["GitHub Authentication Status:", auth_output])
    for line in auth_output.splitlines():
        if "Logged in to github.com" in line:
            return line.strip()
    return "You Are Not Logged In𝕏❌"

class BranchSelectDialog(CenteredDialog):
    def __init__(self, parent, title, branches, default_branch=""):
        self.branches = branches
        self.default_branch = default_branch
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        self.branch_var = tk.StringVar(value=self.default_branch)
        self.combobox = ttk.Combobox(master, textvariable=self.branch_var, values=self.branches)
        self.combobox.pack(padx=10, pady=10)
        return self.combobox

    def apply(self):
        self.result = self.branch_var.get()
        
    def buttonbox(self):
        box = tk.Frame(self)
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

def load_repo_status():
    state_file = "repo_status.json"
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            return json.load(f)
    return {}

def update_repo_status(entry, treeview):
    path = entry.get().strip()
    if not os.path.isdir(path):
        return
    
    repo_status = load_repo_status()
    items = sorted([item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))])
    
    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(os.path.join(full_path, ".git")) and full_path not in repo_status:
            gh_output = run_git_command(
                ["gh", "repo", "view", "--json=isPrivate"], 
                full_path, 
                '{\n    "isPrivate": false\n}'
            )
            is_private = json.loads(gh_output).get("isPrivate", False)
            repo_status[full_path] = is_private
    
    with open("repo_status.json", 'w') as f:
        json.dump(repo_status, f, indent=4)
    
    update_treeview(entry, treeview)

def regenerate_repo_status(entry, treeview, root):
    path = entry.get().strip()
    if not os.path.isdir(path):
        return
    
    repo_status = {}
    items = sorted([item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))])
    treeview.delete(*treeview.get_children())
    
    def process_repo(index=0):
        if index >= len(items):
            with open("repo_status.json", 'w') as f:
                json.dump(repo_status, f, indent=4)
            return
        
        item = items[index]
        full_path = os.path.join(path, item)
        if os.path.isdir(os.path.join(full_path, ".git")):
            gh_output = run_git_command(
                ["gh", "repo", "view", "--json=isPrivate"], 
                full_path, 
                '{\n    "isPrivate": false\n}'
            )
            try:
                is_private = json.loads(gh_output).get("isPrivate", False)
                repo_status[full_path] = is_private
            except json.JSONDecodeError:
                repo_status[full_path] = False
            
            prefix = "🔒 " if repo_status[full_path] else "🌍 "
            treeview.insert("", "end", text=f"{prefix}{item}", values=(item,))
        
        root.after(50, lambda: process_repo(index + 1))
    
    process_repo(0)

def update_single_repo_status(full_path, is_private=None, remove=False):
    repo_status = load_repo_status()
    
    if remove:
        repo_status.pop(full_path, None)
    elif is_private is not None:
        repo_status[full_path] = is_private
    else:
        gh_output = run_git_command(
            ["gh", "repo", "view", "--json=isPrivate"], 
            full_path, 
            '{\n    "isPrivate": false\n}'
        )
        try:
            is_private = json.loads(gh_output).get("isPrivate", False)
            repo_status[full_path] = is_private
        except json.JSONDecodeError:
            repo_status[full_path] = False
    
    with open("repo_status.json", 'w') as f:
        json.dump(repo_status, f, indent=4)
    
    return repo_status