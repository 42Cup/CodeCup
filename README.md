### README
```
## 🚀 Overview
Code Cup ☕ is a lightweight Git repository management tool designed to simplify your workflow with Git and GitHub. Built with Python and Tkinter, it offers an intuitive interface for managing repositories, branches, and GitHub visibility right from your desktop.

## ✨ Main Features
- **Browse Repositories**: Enter a directory path to list all Git repositories within it, with visual indicators for public (🌍) or private (🔒) status.
- **Create and Manage Repos**: Initialize new Git repositories or clone existing ones from GitHub with a few clicks.
- **Branch Operations**: Create, switch, delete, or rollback branches effortlessly.
- **GitHub Integration**: Push changes, toggle repository visibility (public/private), rename, or delete repos directly on GitHub.
- **Real-Time Status**: View branch status, last commit, and changes in a clean text editor pane.

## ✨ Extra Features
- **Context Menu**: Right-click a repository for options like "Branch to New Repo," "Zip Branch," "Open Directory," or "Delete."
- **Color Customization**: Click the 🎨 button and scroll to adjust UI colors (frame background) dynamically.
- **Window Toggle**: Press the "Cl" button to collapse the window to a compact size (75x50) and back.
- **GitHub Auth**: Log in/out of GitHub and see your auth status live in the UI.

```markdown
Requirements: Python 3.x, Tkinter (usually included with Python), subprocess, json, os, shutil

Optional (for full GitHub functionality): Git and GitHub CLI (gh) installed and configured

## 🛠️ Setup (virtual environment)
   Clone or download this repository (git clone https://github.com/42Cup/Code-Cup).
   cd Code-Cup
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt  # If a requirements.txt is added later
   python ui.py

## No virtual environment
   Clone or download this repository (git clone https://github.com/42Cup/Code-Cup).
   cd Code-Cup
   python ui.py

## 📋 Example Usage
1. Enter a directory path (e.g., `/home/user/projects`) in the entry field and press Enter.
2. Select a repository from the list to see its Git status.
3. Use buttons like "New Repo" or "Save Branch" to manage your projects.
4. Right-click a repo for advanced options like zipping a branch or renaming it.
```

## 🤝 Contributing
Feel free to fork, tweak, and enhance Code Cup ☕! Pull requests are welcome—let's brew something great together!

## 📜 License
MIT—free to use, modify, and share however you like!

## ☕ Enjoy!
Created by 42Cup. Grab a cup of coffee and manage your repos with ease!