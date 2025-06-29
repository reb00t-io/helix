# agentic_system.py
import os
from reb00t.helix.progress_manager import ProgressManager
from reb00t.helix.agents.coordinator_agent import CoordinatorAgent

class AgenticSystem:
    def __init__(self):
        self.spec = None
        self.playbook = None
        self.progress = 0
        self.history = []
        self.progress_manager = ProgressManager()
        self._agent = None  # Lazy-loaded RefinementAgent

    def load_spec(self):
        """Loads or updates the living spec document from text or file."""
        file_path = "spec.md"  # Default to reading from spec.md in the current directory
        project_root = self._find_project_root()
        spec_file_path = os.path.join(project_root, file_path)
        spec_text = self._read_spec_file(spec_file_path)

        self.spec = spec_text
        self._record("spec_loaded", {"spec": spec_text, "source": file_path})

    def load_progress(self):
        """Loads the current progress from progress.json file."""
        progress_data = self.progress_manager.load_progress()
        self._record("progress_loaded", {"progress": progress_data})
        return progress_data

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
            current_step = self.current_step()
            self._record("step_advanced", {"step": current_step})

            # Update progress with the new step
            self.update_progress_step(current_step)
            return True
        return False

    def update_progress_step(self, step_name: str, details: list = None, notes: list = None):
        """Updates the progress.json file with new step information."""
        self.progress_manager.advance_to_next_step(
            new_step=step_name,
            details=details or [f"Working on {step_name}"],
            notes=notes or [f"Advanced to {step_name} step"]
        )
        self._record("progress_updated", {
            "step": step_name,
            "details": details,
            "notes": notes
        })

    def add_progress_note(self, note: str):
        """Adds a note to the current progress."""
        self.progress_manager.add_note(note)
        self._record("progress_note_added", {"note": note})

    def add_progress_detail(self, detail: str):
        """Adds a detail to the current progress."""
        self.progress_manager.add_detail(detail)
        self._record("progress_detail_added", {"detail": detail})

    def get_current_progress_step(self) -> str:
        """Returns the current step from progress.json."""
        return self.progress_manager.get_current_step()

    def get_agent(self):
        """Gets or creates the RefinementAgent instance."""
        if self._agent is None:
            self._agent = CoordinatorAgent(self.progress_manager)
        return self._agent

    def run_refinement_cycle(self) -> dict:
        """Runs one complete refinement cycle using the integrated agent."""
        agent = self.get_agent()
        result = agent.run_refinement_cycle(self.spec)
        self._record("refinement_cycle_completed", {"result": result})

        if result.get("error"):
            # If there was an error, log it and add a note
            self.add_progress_note(f"Error in refinement cycle: {result['error']}")

        return result

    def accept_user_feedback(self, feedback: dict) -> dict:
        """Process user feedback on the current refinement plan."""
        agent = self.get_agent()
        result = agent.accept_user_feedback(feedback)
        self._record("user_feedback_processed", {"feedback": feedback, "result": result})
        return result

    def get_current_plan(self) -> dict:
        """Gets the current refinement plan if available."""
        agent = self.get_agent()
        return agent.current_plan

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

    # Load current progress from progress.json
    current_progress = system.load_progress()
    print("Current progress:", current_progress)

    system.load_playbook({
        "steps": [
            {"id": "DRAFT", "goal": "Draft the spec"},
            {"id": "E2E_RED", "goal": "Write red-bar e2e test"},
            {"id": "SCAFFOLD", "goal": "Create basic scaffolding"},
            {"id": "DONE", "goal": "Complete implementation"}
        ]
    })

    # Traditional agent run
    out = system.run_agent({})
    print("Agent Output:", out)

    # Add a progress note
    system.add_progress_note("Agent generated initial output")

    assert system.advance_step()
    assert system.current_step() == "E2E_RED"

    # Check updated progress
    print("Updated progress step:", system.get_current_progress_step())

    print("\n--- Running Refinement Cycle ---")

    # Run a complete refinement cycle
    refinement_result = system.run_refinement_cycle()
    print("Refinement cycle completed:", refinement_result["cycle_completed"])
    print("Steps completed:", refinement_result["steps_completed"])

    if refinement_result["user_feedback_required"]:
        print("User feedback required for plan:")
        plan = system.get_current_plan()
        print(f"Plan: {plan['summary']}")

        # Simulate user approval
        feedback = {"approved": True}
        feedback_result = system.accept_user_feedback(feedback)
        print(f"Feedback processed: {feedback_result['status']}")

        # Run the cycle again after approval
        final_result = system.run_refinement_cycle()
        print("Final refinement result:", final_result["cycle_completed"])
