# agentic_system.py

class AgenticSystem:
    def __init__(self):
        self.spec = None
        self.playbook = None
        self.progress = 0
        self.history = []

    def load_spec(self, spec_text: str):
        """Loads or updates the living spec document."""
        self.spec = spec_text
        self._record("spec_loaded", {"spec": spec_text})

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
    system.load_spec("## System Spec\nSteps: Draft, E2E, Scaffold, Logic, Infra, Done")
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
