import json
import os
from reb00t.common.utils.git_utils import chdir_to_project_root

project_config = None

def cfg_get(key, default=None):
    """
    Get a configuration value from the project config.
    If the key does not exist, return the default value.
    """
    assert project_config is not None, "Project config not loaded. Call init_process() first."
    keys = key.split('.')
    value = project_config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value

def cfg_set(key, value):
    """
    Set a configuration value in the project config and write it to disk.
    Supports nested keys using dot notation.
    """
    assert project_config is not None, "Project config not loaded. Call init_process() first."
    keys = key.split('.')
    d = project_config
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            d[k] = {}
        d = d[k]
    d[keys[-1]] = value
    with open("coda.json", "w") as f:
        json.dump(project_config, f, indent=4)

def cfg_name():
    return cfg_get("name", None)

def cfg_security_review():
    return cfg_get("security_review", "undefined") != "none"

def cfg_get_protected_branches():
    return set(cfg_get("protected_branches", []))

def cfg_get_main_branch():
    return cfg_get("main_branch", "main")

def cfg_get_last_branch():
    return cfg_get("last_branch", None)

def cfg_set_last_branch(branch):
    """
    Set the last used branch in the project config.
    """
    cfg_set("last_branch", branch)

def _load_project_config():
    # no config is ok
    if not os.path.exists("coda.json"):
        return {}

    with open("coda.json", "r") as f:
        return json.load(f)


def init_process():
    chdir_to_project_root()

    # load project config in project root
    global project_config
    project_config = _load_project_config()

    # get the name of the project from git
    project_config["name"] = os.path.basename(os.getcwd())
