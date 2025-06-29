# agentic_system.py
import os

class AgenticSystem:
    def __init__(self):
        self.spec = None
        self.playbook = None
        self.progress = 0
        self.history = []

    def load_spec(self):
        """Loads or updates the living spec document from text or file."""
        file_path = "spec.md"  # Default to reading from spec.md in the current directory
        project_root = self._find_project_root()
        spec_file_path = os.path.join(project_root, file_path)
        spec_text = self._read_spec_file(spec_file_path)

        self.spec = spec_text
        self._record("spec_loaded", {"spec": spec_text, "source": file_path})

    def _read_spec_file(self, file_path: str) -> str:
        """Reads the spec from a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Spec file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading spec file {file_path}: {str(e)}")

    def _find_project_root(self) -> str:
        """Finds the project root directory (where spec.md should be located)."""
        current_dir = os.getcwd()
        # Go up directories until we find spec.md or reach the root
        while current_dir != os.path.dirname(current_dir):  # Not at filesystem root
            if os.path.exists(os.path.join(current_dir, "spec.md")):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        # If not found, assume current directory or go up one more level
        return os.path.dirname(os.path.dirname(current_dir))

    def load_playbook(self, playbook: dict):
        """Loads the playbook of steps and rules."""
        self.playbook = playbook
        self._record("playbook_loaded", {"playbook": playbook})

    def advance_step(self):
        """Attempts to advance to the next playbook step, if exit condition met."""
        if self._can_advance():
            self.progress += 1
            self._record("step_advanced", {"step": self.current_step()})
            return True
        return False

    def current_step(self):
        return self.playbook['steps'][self.progress]['id']

    def run_agent(self, context):
        """Triggers the agent LLM to generate code/tests/commits for the current step."""
        output = f"# TODO for step {self.current_step()}\n"
        self._record("agent_ran", {"step": self.current_step(), "output": output})
        return output

    def _can_advance(self):
        # For the mock, let’s just allow advancing every time.
        return True

    def _record(self, event_type, payload):
        self.history.append({"event": event_type, "data": payload})

    def get_history(self):
        return self.history

# --- Example usage: ---
if __name__ == "__main__":
    system = AgenticSystem()
    # Load the actual spec from spec.md file (will use default path)
    system.load_spec()
    system.load_playbook({
        "steps": [
            {"id": "DRAFT", "goal": "..."},
            {"id": "E2E_RED", "goal": "..."},
            {"id": "SCAFFOLD", "goal": "..."},
            {"id": "DONE", "goal": "..."}
        ]
    })
    out = system.run_agent({})
    print("Agent Output:", out)
    assert system.advance_step()
    assert system.current_step() == "E2E_RED"
