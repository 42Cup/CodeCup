import tkinter as tk
from tkinter import simpledialog, messagebox
from logic import run_in_xterm_zip, load_repo_status, BranchSelectDialog, update_treeview, on_treeview_select, run_in_xterm, confirm_and_run_command, get_gh_username, update_repo_status, select_new_folder
import os # Only import BranchSelectDialog separately
import json
import shutil
import subprocess  
from logic import require_gh_login

def _get_valid_path(entry, treeview, require_selection=True):
    base_path = entry.get().strip()
    if not base_path or not os.path.isdir(base_path):
        messagebox.showerror("Error", "Invalid base directory path")
        return None, None
    selection = treeview.selection()
    if require_selection and not selection:
        messagebox.showerror("Error", "Please select a folder")
        return None, None
    selected_item = treeview.item(selection[0])["values"][0] if selection else ""  # Use values[0] instead of text
    return base_path, os.path.join(base_path, selected_item) if selected_item else base_path

def git_init(entry, treeview, globals_dict):
    folder_name = simpledialog.askstring("Git Init", "Enter folder name:")
    if folder_name is None: return
    base_path, full_path = _get_valid_path(entry, treeview, False)
    if not base_path: return
    confirm_and_run_command(f"git init {full_path}", base_path, globals_dict)
    update_treeview(entry, treeview)

def gh_repo_create(entry, treeview, globals_dict):
    username = simpledialog.askstring("GitHub Repo Create", "Enter your GitHub username:")
    if username is None: return
    project_name = simpledialog.askstring("GitHub Repo Create", "Enter project name:")
    if project_name is None: return
    base_path, full_path = _get_valid_path(entry, treeview)
    if not base_path: return
    visibility = "--private" if messagebox.askyesno("GitHub Repo Create", "Make repository private?") else "--public"
    confirm_and_run_command(f"gh repo create {username}/{project_name} {visibility} --source=. --remote=origin", full_path, globals_dict)











# 1- New Repo
def create_new_repo(globals_dict):
    if not require_gh_login(): return
    folder_name = simpledialog.askstring("New Repo", "name")
    if folder_name is None:
        return
    
    base_path = globals_dict['entry'].get().strip()
    if not base_path or not os.path.isdir(base_path):
        messagebox.showerror("Error", "Please enter a valid base directory path first")
        return
    full_path = os.path.join(base_path, folder_name)
    
    default_username = get_gh_username()
    username = default_username
    
    project_name = folder_name
    
    is_private = messagebox.askyesno("New Repo", "Private?")
    visibility = "--private" if is_private else "--public"
    
    init_command = f"git init {full_path}"
    create_command = f"gh repo create {username}/{project_name} {visibility} --source=. --remote=origin"
    
    full_command = f"{init_command} && cd {full_path} && {create_command}"
    confirm_and_run_command(full_command, base_path, globals_dict, folder_name)

# 2- Save Branch
def git_push(entry, treeview, globals_dict):
    if not require_gh_login(): return
    base_path, full_path = _get_valid_path(entry, treeview)
    if not base_path: return
    try:
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=full_path, text=True).strip()
    except subprocess.CalledProcessError:
        current_branch = "master"
    cmd_parts = []
    # Default 'git add .' to Yes, skip prompt
    cmd_parts.append("git add .")
    # Keep commit message prompt as-is
    commit_msg = simpledialog.askstring("Save Branch", "Enter commit message:", initialvalue="updated")
    if commit_msg is None: return
    if commit_msg: cmd_parts.append(f"git commit -m \"{commit_msg}\"")
    # Default remote to "origin", skip prompt
    remote = "origin"
    # Default branch to current_branch, skip prompt
    branch = current_branch
    # Default -u option to Yes, skip prompt
    u_option = "-u"
    cmd_parts.append(f"git push {u_option} {remote} {branch}".strip())
    confirm_and_run_command(" && ".join(cmd_parts), full_path, globals_dict)


    # def git_push(entry, treeview, globals_dict):
    #     base_path, full_path = _get_valid_path(entry, treeview)
    #     if not base_path: return
    #     try:
    #         current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=full_path, text=True).strip()
    #     except subprocess.CalledProcessError:
    #         current_branch = "master"
    #     cmd_parts = []
    #     add_files = messagebox.askyesno("Save Branch", "Run 'git add .' first?")
    #     if not add_files and add_files is not None: return
    #     if add_files: cmd_parts.append("git add .")
    #     commit_msg = simpledialog.askstring("Save Branch", "Enter commit message:", initialvalue="updated")
    #     if commit_msg is None: return
    #     if commit_msg: cmd_parts.append(f"git commit -m \"{commit_msg}\"")
    #     remote = simpledialog.askstring("Save Branch", "Enter remote name (e.g., origin):", initialvalue="origin")
    #     if remote is None: return
    #     remote = remote or "origin"
    #     branch = simpledialog.askstring("Save Branch", "Enter branch name:", initialvalue=current_branch)
    #     if branch is None: return
    #     branch = branch or current_branch
    #     u_option = "-u" if messagebox.askyesno("Save Branch", "Use -u option to set upstream?") else ""
    #     cmd_parts.append(f"git push {u_option} {remote} {branch}".strip())
    #     confirm_and_run_command(" && ".join(cmd_parts), full_path, globals_dict)

# 3- Swap Branch
def git_checkout(entry, treeview, globals_dict, root):
    base_path, full_path = _get_valid_path(entry, treeview)
    if not base_path: return
    try:
        branches = [line.strip().replace('*', '').strip() for line in subprocess.check_output(["git", "branch"], cwd=full_path, text=True).splitlines() if line.strip()]
        if not branches: return messagebox.showinfo("No Branches", "No existing branches found in this repository")
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=full_path, text=True).strip()
        branch_name = BranchSelectDialog(root, "Change Branch", branches, current_branch).result
        if branch_name is None: return
        if branch_name:
            confirm_and_run_command(f"git checkout {branch_name}", full_path, globals_dict)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Could not retrieve branch list")

#4- New Branch
def git_branch(entry, treeview, globals_dict):
    if not require_gh_login(): return
    base_path, full_path = _get_valid_path(entry, treeview)
    if not base_path: return
    branch_name = simpledialog.askstring("New Branch", "name")
    if branch_name is None: return
    if branch_name:
        cmd = f"git branch {branch_name} && git checkout {branch_name} && git push -u origin {branch_name}"
        confirm_and_run_command(cmd, full_path, globals_dict)

# 5- Drop Branch
def git_branch_delete(entry, treeview, globals_dict, root):
    if not require_gh_login(): return
    base_path, full_path = _get_valid_path(entry, treeview)
    if not base_path: return
    try:
        # Get branch list and current branch
        branches = [line.strip().replace('*', '').strip() for line in subprocess.check_output(["git", "branch"], cwd=full_path, text=True).splitlines() if line.strip()]
        if not branches: return messagebox.showinfo("No Branches", "No branches found to delete")
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=full_path, text=True).strip()
        
        branch_name = BranchSelectDialog(root, "Drop Branch", branches, "").result
        if branch_name is None: return
        if branch_name:
            if branch_name == current_branch:
                # If trying to delete the current branch, switch to another first
                other_branches = [b for b in branches if b != branch_name]
                if not other_branches:
                    messagebox.showerror("Error", f"Cannot delete '{branch_name}'—it's the only branch!")
                    return
                # Switch to the first available branch
                confirm_and_run_command(f"git checkout {other_branches[0]} && git branch -d {branch_name} && git push origin --delete {branch_name}", full_path, globals_dict, prompt_message=f"Switching to '{other_branches[0]}' before deleting '{branch_name}'")
            else:
                confirm_and_run_command(f"git branch -d {branch_name} && git push origin --delete {branch_name}", full_path, globals_dict, prompt_message=f"Deleting branch '{branch_name}'")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to delete branch: {e.output or 'Unknown error'}")

    # def git_branch_delete(entry, treeview, globals_dict, root):
    #     base_path, full_path = _get_valid_path(entry, treeview)
    #     if not base_path: return
    #     try:
    #         branches = [line.strip().replace('*', '').strip() for line in subprocess.check_output(["git", "branch"], cwd=full_path, text=True).splitlines() if line.strip()]
    #         if not branches: return messagebox.showinfo("No Branches", "No branches found to delete")
    #         branch_name = BranchSelectDialog(root, "Drop Branch", branches, "").result
    #         if branch_name is None: return
    #         if branch_name:
    #             confirm_and_run_command(f"git branch -d {branch_name} && git push origin --delete {branch_name}", full_path, globals_dict)
    #     except subprocess.CalledProcessError:
    #         messagebox.showerror("Error", "Could not retrieve branch list")

# 6- Fetch Branch
def git_rollback(entry, treeview, globals_dict):
    base_path, full_path = _get_valid_path(entry, treeview)
    if not base_path: return
    try:
        branches = [line.strip().replace('*', '').strip() for line in subprocess.check_output(["git", "branch"], cwd=full_path, text=True).splitlines() if line.strip()]
        if not branches: return messagebox.showinfo("No Branches", "No branches found to rollback to")
        branch_name = BranchSelectDialog(globals_dict['root'], "Fetch Branch", branches, "").result
        if branch_name is None: return
        if branch_name:
            if not messagebox.askyesno("Confirm Rollback", f"This will wipe all files (except .git) and replace with files from '{branch_name}'. Proceed?"):
                return
            # Wipe all files except .git
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if item != ".git":
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            # Execute rollback commands directly
            subprocess.run(["git", "checkout", branch_name, "--", "."], cwd=full_path, check=True)
            subprocess.run(["git", "reset"], cwd=full_path, check=True)
            # Update UI
            globals_dict['root'].after(100, lambda: [
                # update_treeview(entry, treeview),  # Refresh the Treeview
                on_treeview_select(entry, treeview, globals_dict['text_editor'], globals_dict['auth_label'])  # Update right panel
            ])
            messagebox.showinfo("Success", f"Rolled back files to state of branch '{branch_name}'.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Rollback failed: {e.output or 'Unknown error'}")



 






# cm-1- Branch 2 New Repo
def branch_to_new_repo(base_path, selected_item, full_path, globals_dict):
    if not require_gh_login(): return
    from logic import run_git_command, update_single_repo_status
    import os
    
    current_branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], full_path, "main").strip()
    if not current_branch:
        messagebox.showerror("Error", "Could not determine current branch.")
        return
    
    new_repo_name = simpledialog.askstring("Branch 2 New Repo", f"Enter new repo name (from branch '{current_branch}'):", initialvalue=f"{selected_item}_{current_branch}")
    if not new_repo_name:
        return
    
    new_full_path = os.path.join(base_path, new_repo_name)
    if os.path.exists(new_full_path):
        messagebox.showerror("Error", f"Folder '{new_repo_name}' already exists!")
        return
    
    default_username = get_gh_username()
    username = default_username
    
    project_name = new_repo_name
    
    is_private = messagebox.askyesno("Create New Repo on GitHub", "Make repository private?")
    visibility = "--private" if is_private else "--public"
    
    full_command = (
        f"mkdir '{new_full_path}' && "
        f"git archive {current_branch} --output='{new_full_path}/{new_repo_name}_{current_branch}.zip' && "
        f"unzip '{new_full_path}/{new_repo_name}_{current_branch}.zip' -d '{new_full_path}' && "
        f"rm '{new_full_path}/{new_repo_name}_{current_branch}.zip' && "
        f"git init '{new_full_path}' && "
        f"cd '{new_full_path}' && git add . && git commit -m 'Initial commit from branch {current_branch}' && "
        f"gh repo create {username}/{project_name} {visibility} --source=. --remote=origin && "
        f"git push -u origin master"
    )
    
    if confirm_and_run_command(full_command, full_path, globals_dict, new_repo_name, prompt_message=f"Creating new repo '{new_repo_name}' from branch '{current_branch}'"):
        messagebox.showinfo("Success", f"New repo '{new_repo_name}' created from branch '{current_branch}'!")
        # Update repo_status.json directly with the known visibility
        update_single_repo_status(new_full_path, is_private)

# cm-2- Zip From Branch
def zip_from_branch(base_path, selected_item, full_path, globals_dict):
    from logic import run_git_command
    current_branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], full_path, "main").strip()
    zip_filename = os.path.join(base_path, f"{selected_item}_{current_branch}.zip")
    command = f"git archive {current_branch} --output={zip_filename}"
    run_in_xterm_zip(command, full_path)
    messagebox.showinfo(".Zip Created", zip_filename)

# cm-3-  Repo Link
def copy_repo_link(globals_dict, selected_item):
    globals_dict['root'].clipboard_clear()
    globals_dict['root'].clipboard_append(f"https://github.com/{get_gh_username()}/{selected_item}")

# cm-4- Open Directory 
def run_claude_code(full_path, base_path):
    subprocess.Popen(f"xterm -e \"cd {full_path} && claude\"", shell=True)

# cm-5-  Claude Code
def open_directory(full_path):
    if os.name == 'nt':
        os.startfile(full_path)
    elif os.name == 'posix':
        os.system(f"open '{full_path}'")
    else:
        os.system(f"xdg-open '{full_path}'")

# cm-6- Go Public
def go_public(globals_dict, selected_item, full_path):
    if not require_gh_login(): return
    from logic import update_single_repo_status
    full_command = f"gh repo edit --visibility public"
    if confirm_and_run_command(full_command, full_path, globals_dict, prompt_message=f"Setting '{selected_item}' to public"):
        # Update repo_status.json to reflect public status
        update_single_repo_status(full_path, is_private=False)
        # Refresh the treeview immediately
        globals_dict['root'].after(100, lambda: update_treeview(globals_dict['entry'], globals_dict['treeview']))

# cm-7- Go Private
def go_private(globals_dict, selected_item, full_path):
    if not require_gh_login(): return
    from logic import update_single_repo_status
    full_command = f"gh repo edit --visibility private"
    if confirm_and_run_command(full_command, full_path, globals_dict, prompt_message=f"Setting '{selected_item}' to private"):
        # Update repo_status.json to reflect private status
        update_single_repo_status(full_path, is_private=True)
        # Refresh the treeview immediately
        globals_dict['root'].after(100, lambda: update_treeview(globals_dict['entry'], globals_dict['treeview']))

# cm-8- Rename
def rename_repo(globals_dict, selected_item, base_path, full_path):
    if not require_gh_login(): return
    from logic import update_single_repo_status
    new_name = simpledialog.askstring("Rename Repository", f"Enter new name for '{selected_item}':", initialvalue=selected_item)
    if new_name and new_name != selected_item:
        new_full_path = os.path.join(base_path, new_name)
        if os.path.exists(new_full_path):
            messagebox.showerror("Error", f"A folder named '{new_name}' already exists!")
            return
        if messagebox.askyesno("Confirm Rename", f"Rename '{selected_item}' to '{new_name}' locally and on GitHub?"):
            try:
                # Get current visibility before renaming
                repo_status = load_repo_status()
                current_visibility = repo_status.get(full_path, False)
                
                # Rename local folder
                os.rename(full_path, new_full_path)
                # Update GitHub repo name if it exists
                username = get_gh_username()
                run_in_xterm(f"gh repo rename {new_name} --repo {username}/{selected_item} --yes", new_full_path)
                # Update repo_status.json with new path
                update_single_repo_status(full_path, remove=True)  # Remove old entry
                update_single_repo_status(new_full_path, is_private=current_visibility)  # Add new entry
                # Refresh treeview
                globals_dict['root'].after(1000, lambda: update_treeview(globals_dict['entry'], globals_dict['treeview']))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename repository: {str(e)}")

# cm-9- Delete
def confirm_delete(globals_dict, selected_item):
    if not require_gh_login(): return
    from logic import update_single_repo_status
    base_path = globals_dict['entry'].get().strip()
    if not base_path or not os.path.isdir(base_path):
        messagebox.showerror("Error", "Invalid base directory path")
        return
    full_path = os.path.join(base_path, selected_item)
    if not os.path.isdir(full_path): 
        messagebox.showerror("Error", f"Directory {full_path} does not exist")
        return
    if not messagebox.askyesno("💥DELETE REPO💥💥💥💥💥💥💥💥💥💥", f"DELETE '{selected_item}' PERMANENTLY?\n\n   ALL COPIES ONLINE\n\nAND COMPUTER DELETED \n\n\n☠️⚠️ GONE FOREVER ⚠️☠️ \n\n      ARE YOU SURE?"):
        return
    user_input = simpledialog.askstring("ARE YOU SURE? 💀", f"Type 'delete {selected_item}' to confirm:")
    if user_input != f"delete {selected_item}":
        return
    
    try:
        repo_path = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=full_path, text=True).strip().split('github.com/')[-1].replace('.git', '')
        full_command = f"gh repo delete {repo_path} --yes && rm -rf '{full_path}'"
        if confirm_and_run_command(full_command, base_path, globals_dict, prompt_message=f"Deleting '{selected_item}' from GitHub and locally"):
            messagebox.showinfo("Success", f"'{selected_item}' DELETED FOREVER")
            # Remove from repo_status.json
            update_single_repo_status(full_path, remove=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to retrieve repo URL:\n{e.stderr or 'Unknown error'}")
    finally:
        update_treeview(globals_dict['entry'], globals_dict['treeview'])

# bb-10- Clone
class CloneDialog(simpledialog.Dialog):
    def __init__(self, parent, title, globals_dict):
        self.globals_dict = globals_dict
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="GitHub URL:").pack()
        self.url_entry = tk.Entry(master)
        self.url_entry.pack()
        return self.url_entry

    def buttonbox(self):
        box = tk.Frame(self)
        w = tk.Button(box, text="Clone", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def apply(self):
        url = self.url_entry.get().strip()
        if url:
            base_path = self.globals_dict['entry'].get().strip()
            if base_path and os.path.isdir(base_path):
                # Extract repo name from URL (e.g., "user/repo" or "https://github.com/user/repo.git")
                repo_name = url.split('/')[-1].replace('.git', '').strip()
                full_path = os.path.join(base_path, repo_name)
                
                # Run git clone synchronously and check if it succeeds
                command = f"git clone {url}"
                try:
                    result = subprocess.run(
                        command, 
                        cwd=base_path, 
                        shell=True, 
                        text=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                    )
                    if result.returncode == 0 and os.path.isdir(full_path):
                        # Clone succeeded and directory exists, update repo status
                        from logic import update_single_repo_status
                        update_single_repo_status(full_path)  # Queries GitHub for status
                    else:
                        # Clone failed, show error with stderr
                        messagebox.showerror("Clone Failed", f"Error cloning repository:\n{result.stderr}")
                        return
                except Exception as e:
                    messagebox.showerror("Clone Error", f"Failed to execute clone command:\n{str(e)}")
                    return
                
                # Refresh UI after successful clone
                self.globals_dict['root'].after(100, lambda: [
                    update_treeview(self.globals_dict['entry'], self.globals_dict['treeview']),
                    on_treeview_select(
                        self.globals_dict['entry'], 
                        self.globals_dict['treeview'], 
                        self.globals_dict['text_editor'], 
                        self.globals_dict['auth_label']
                    )
                ])
            else:
                messagebox.showerror("Error", "Invalid base directory")

