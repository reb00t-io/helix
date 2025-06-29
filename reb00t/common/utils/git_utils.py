import os
import subprocess
import sys

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import RadioList, Box, Frame

import pathspec

def get_upstream_branch(branch):
    """
    Get the upstream branch for a given local branch.
    Returns the upstream branch name or None if not set.
    """
    # Then: check for upstream
    try:
        upstream_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"],
            capture_output=True, text=True
        )
        is_active = (upstream_proc.returncode == 0)
        upstream_branch = upstream_proc.stdout.strip()
    except Exception:
        upstream_branch = None
        is_active = False

    return upstream_branch, is_active

def get_dead_branches(local_branches, main_branch):
    local_merged = []
    no_upstream = []
    upstream = []

    # 3. For each branch, check if it has a remote tracking branch
    # 4. If no remote, or if merged upstream, delete; else skip
    # Get merged branches (merged into origin/main)
    try:
        merged_proc = subprocess.run(
            ["git", "branch", "--merged", f"origin/{main_branch}"],
            capture_output=True, text=True, check=True
        )
        merged_branches = set(
            line.strip().lstrip("* ").strip()
            for line in merged_proc.stdout.splitlines() if line.strip()
        )
    except subprocess.CalledProcessError:
        print("\033[1;31mFailed to get merged branches.\033[0m")
        merged_branches = set()

    for branch in local_branches:
        if branch == main_branch:
            continue

        # First: check if merged into origin/main (even if it has no remote)
        if branch in merged_branches:
            local_merged.append(branch)
            continue

        upstream_branch, has_upstream = get_upstream_branch(branch)

        if not has_upstream:
            no_upstream.append(branch)
        else:
            upstream.append(upstream_branch)

    return no_upstream, local_merged, upstream

def prune_deleted_remote_branches(log_file=None):
    # 1. Prune deleted remote branches
    print("\033[1;36mPruning deleted remote branches (git fetch -p)...\033[0m")
    try:
        subprocess.run(["git", "fetch", "-p"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("\033[1;31mFailed to fetch/prune remotes.\033[0m")
        if log_file:
            with open(log_file, "a") as f:
                f.write("Failed to fetch/prune remotes.\n")
        return False

def get_local_branches(remote=False, log_file=None):
    try:
        if remote:
            result = subprocess.run(
                ["git", "branch", "-r"],
                capture_output=True, text=True, check=True
            )
        else:
            result = subprocess.run(
                ["git", "branch", "--list"],
                capture_output=True, text=True, check=True
            )
    except subprocess.CalledProcessError:
        raise Exception("Error fetching git branches.")

    branches = []
    current_idx = 0
    for i, line in enumerate(result.stdout.splitlines()):
        line = line.strip()
        if remote:
            # skip HEAD -> origin/HEAD lines
            if "->" in line:
                continue
            branch = line
        else:
            if line.startswith("*"):
                branch = line[2:].strip()
                current_idx = len(branches)
            else:
                branch = line
        branches.append(branch)

    if not branches:
        print("No local branches found.")
        if log_file:
            with open(log_file, "a") as f:
                f.write("No local branches found.\n")

    return branches, current_idx


def chdir_to_project_root():
    # Get project root using 'git rev-parse --show-toplevel'
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    root = result.stdout.strip()
    if not root:
        print("Failed to find project root.")
        sys.exit(1)
    os.chdir(root)


def _load_gitignore_spec(folder):
    """
    Load .gitignore patterns from the current folder only.
    Returns a PathSpec object representing the ignore patterns for this folder.
    """

    # copy parent patterns if provided
    patterns = []

    gitignore_path = os.path.join(folder, '.gitignore')
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r') as f:
            patterns.extend(f.read().splitlines())
    spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    return spec

def _ignore_file(full_path, ignore_specs):
    """
    Check if the given file path should be ignored based on the provided ignore specs.
    """
    for spec, spec_root in ignore_specs:
        rel_to_root = os.path.relpath(full_path, spec_root)
        if spec.match_file(rel_to_root):
            return True

    return False

def _list_code_files_recursive(folder, extensions, ignore_specs=[], level=0, files_max_size=None):
    """
    Recursively returns a list of code files in the given folder and its subdirectories,
    filtered by the provided file extensions, ordered by last modification time (descending).
    Supports nested .gitignore files by combining ignore patterns hierarchically.
    Example: extensions = [".py", ".js"]
    """
    spec = _load_gitignore_spec(folder)
    ignore_specs.append((spec, folder))

    result = []
    try:
        entries = os.listdir(folder)
    except OSError:
        return result  # skip folders we can't access

    for entry in entries:
        full_path = os.path.join(folder, entry)
        rel_path = entry  # relative to current folder

        if _ignore_file(full_path, ignore_specs):
            continue  # skip ignored files or directories

        if os.path.isdir(full_path):
            sub_tree = _list_code_files_recursive(full_path, extensions, ignore_specs, level + 1, files_max_size)
            if sub_tree:
                # If subdirectory has code files, add the directory
                mtime = os.path.getmtime(full_path)
                result.append((level, rel_path + "/", full_path, mtime, 0))
                result.extend(sub_tree)
        elif os.path.isfile(full_path):
            if any(entry.lower().endswith(ext.lower()) for ext in extensions):
                try:
                    file_size = os.path.getsize(full_path)
                    if files_max_size is not None and file_size > files_max_size:
                        print(f"Skipping {full_path} due to size limit")
                        continue  # skip files that exceed max size
                    mtime = os.path.getmtime(full_path)
                    result.append((level, rel_path, full_path, mtime, file_size))
                except OSError:
                    continue  # skip files we can't access

    return result

def list_code_files(extensions, ignore_specs=[], files_max_size=None):
    """
    Wrapper function that starts recursive search from the current working directory.
    """
    return _list_code_files_recursive(os.getcwd(), extensions, ignore_specs=ignore_specs, files_max_size=files_max_size)

async def select_branch(branches, current_branch_idx, remote, current_selection=None):
    mode = {"remote": remote}
    saved_selection = {"local": None, "remote": None}
    saved_selection["remote" if remote else "local"] = branches[current_branch_idx]

    radio_list = RadioList([(b, b) for b in branches])
    radio_list.current_value = branches[current_branch_idx]
    if current_selection is not None and current_selection in branches:
        radio_list._selected_index = branches.index(current_selection)
    else:
        radio_list._selected_index = current_branch_idx
    radio_list.control.key_bindings.remove("enter")
    kb = KeyBindings()

    def reload_branches():
        try:
            new_branches, new_idx = get_local_branches(remote=mode["remote"])
        except Exception as e:
            # ignore reload errors, keep old branches
            return
        radio_list.values = [(b, b) for b in new_branches]
        # restore previous selection if possible
        prev_sel = saved_selection["remote" if mode["remote"] else "local"]
        if prev_sel in new_branches:
            radio_list.current_value = prev_sel
        else:
            radio_list.current_value = new_branches[0] if new_branches else None
        saved_selection["remote" if mode["remote"] else "local"] = radio_list.current_value

    @kb.add("c-c")
    @kb.add("escape")
    @kb.add("q")
    def _exit(event):
        event.app.exit(result=None)

    @kb.add("r")
    def _toggle_remote(event):
        # save current selection
        saved_selection["remote" if mode["remote"] else "local"] = radio_list.current_value
        mode["remote"] = not mode["remote"]
        reload_branches()
        # update frame title
        event.app.layout.container.title = f"Select a branch ({'remote' if mode['remote'] else 'local'}) (ESC/q to abort, r to toggle)"

    @kb.add("enter")
    def _accept(event):
        radio_list._handle_enter()
        event.app.exit(result=radio_list.current_value)

    frame = Frame(Box(radio_list, padding=1), title=f"Select a branch ({'remote' if remote else 'local'}) (ESC/q to abort, r to toggle)")
    layout = Layout(frame, focused_element=radio_list)
    app = Application(layout=layout, key_bindings=kb, full_screen=False)
    result = await app.run_async()
    return result
