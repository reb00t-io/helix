import sys

def ask_yes_no(prompt, default_yes=True, exit_on_cancel=True):
    """Ask a yes/no question via input(), return True for yes, False for no. Ctrl-C cleanly exits."""
    default = "Y/n" if default_yes else "y/N"

    if exit_on_cancel:
        try:
            answer = input(f"{prompt} [{default}]: ").strip().lower()
        except KeyboardInterrupt:
            print("\nCancelled by user (Ctrl-C).")
            sys.exit(0)
    else:
        answer = input(f"{prompt} [{default}]: ").strip().lower()

    if not answer:
        return default_yes
    return answer == "y"
