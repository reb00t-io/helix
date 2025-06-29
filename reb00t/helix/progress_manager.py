# progress.py
import os
import json

class ProgressManager:
    def __init__(self, progress_file_path: str = "progress.json"):
        self.progress_file_path = progress_file_path

    def load_progress(self) -> dict:
        """Loads the current progress from progress.json file."""
        if not os.path.exists(self.progress_file_path):
            return {
                "task": "",
                "step": "A: Preparation, step 1",
                "details": [],
                "notes": []
            }

        try:
            with open(self.progress_file_path, 'r', encoding='utf-8') as file:
                progress = json.load(file)

            # Ensure all required fields exist
            if "task" not in progress:
                progress["task"] = ""
            if "step" not in progress:
                progress["step"] = "A: Preparation, step 1"
            if "details" not in progress:
                progress["details"] = []
            if "notes" not in progress:
                progress["notes"] = []

            return progress
        except (json.JSONDecodeError, Exception) as e:
            raise Exception(f"Error reading progress file {self.progress_file_path}: {str(e)}")

    def update_progress(self, task: str = None, step: str = None, details: list = None, notes: list = None):
        """Updates the progress.json file with new information."""
        current_progress = self.load_progress()

        # Update fields if provided
        if task is not None:
            current_progress["task"] = task
        if step is not None:
            current_progress["step"] = step
        if details is not None:
            current_progress["details"] = details
        if notes is not None:
            current_progress["notes"] = notes

        # Write updated progress back to file
        self._write_progress(current_progress)

    def _write_progress(self, progress: dict):
        """Writes the progress data to progress.json file."""
        try:
            with open(self.progress_file_path, 'w', encoding='utf-8') as file:
                json.dump(progress, file, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Error writing progress file {self.progress_file_path}: {str(e)}")

    def get_current_step(self) -> str:
        """Returns the current step from progress.json."""
        progress = self.load_progress()
        return progress["step"]

    def get_current_task(self) -> str:
        """Returns the current task from progress.json."""
        progress = self.load_progress()
        return progress.get("task", "")

    def advance_to_next_step(self, new_step: str, details: list = None, notes: list = None):
        """Advances to the next step and updates progress.json."""
        self.update_progress(step=new_step, details=details, notes=notes)

    def set_task(self, task: str):
        """Sets the current task in progress.json."""
        self.update_progress(task=task)

    def add_note(self, note: str):
        """Adds a note to the current progress."""
        current_progress = self.load_progress()
        current_progress["notes"].append(note)
        self.update_progress(notes=current_progress["notes"])

    def add_detail(self, detail: str):
        """Adds a detail to the current progress."""
        current_progress = self.load_progress()
        current_progress["details"].append(detail)
        self.update_progress(details=current_progress["details"])


# --- Example usage: ---
if __name__ == "__main__":
    # Example usage
    pm = ProgressManager()

    # Load current progress
    progress = pm.load_progress()
    print("Current progress:", progress)

    # Update progress
    pm.update_progress(
        task="tasks/001-hello-world.json",
        step="B: Refinement, step 2",
        details=["Adjusting e2e test according to plan", "Implementing new features"],
        notes=["Previous step completed successfully", "Ready for implementation phase"]
    )

    print("Updated step:", pm.get_current_step())
    print("Current task:", pm.get_current_task())

    # Add a note
    pm.add_note("Implementation progressing well")
    print("After adding note:", pm.load_progress())
