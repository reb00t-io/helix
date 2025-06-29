# progress.py
import os
import re

class ProgressManager:
    def __init__(self, progress_file_path: str = "progress.md"):
        self.progress_file_path = progress_file_path

    def load_progress(self) -> dict:
        """Loads the current progress from progress.md file."""
        if not os.path.exists(self.progress_file_path):
            return {
                "step": "A: Preparation, step 1",
                "details": [],
                "notes": []
            }

        try:
            with open(self.progress_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            return self._parse_progress(content)
        except Exception as e:
            raise Exception(f"Error reading progress file {self.progress_file_path}: {str(e)}")

    def _parse_progress(self, content: str) -> dict:
        """Parses the progress.md content into a structured format."""
        progress = {
            "step": "",
            "details": [],
            "notes": []
        }

        # Split content into sections
        sections = re.split(r'^## ', content, flags=re.MULTILINE)

        for section in sections:
            if section.strip().startswith('Step'):
                # Extract step information
                lines = section.strip().split('\n')
                if len(lines) > 1:
                    progress["step"] = lines[1].strip()

            elif section.strip().startswith('Details'):
                # Extract details
                lines = section.strip().split('\n')[1:]  # Skip the "Details" header
                details = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('##'):
                        # Remove markdown list markers
                        line = re.sub(r'^[-*+]\s*', '', line)
                        details.append(line)
                progress["details"] = details

            elif section.strip().startswith('Notes'):
                # Extract notes
                lines = section.strip().split('\n')[1:]  # Skip the "Notes" header
                notes = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('##'):
                        # Remove markdown list markers
                        line = re.sub(r'^[-*+]\s*', '', line)
                        notes.append(line)
                progress["notes"] = notes

        return progress

    def update_progress(self, step: str = None, details: list = None, notes: list = None):
        """Updates the progress.md file with new information."""
        current_progress = self.load_progress()

        # Update fields if provided
        if step is not None:
            current_progress["step"] = step
        if details is not None:
            current_progress["details"] = details
        if notes is not None:
            current_progress["notes"] = notes

        # Write updated progress back to file
        self._write_progress(current_progress)

    def _write_progress(self, progress: dict):
        """Writes the progress data to progress.md file."""
        content = "# Progress\n\n"

        # Add Step section
        content += "## Step\n"
        content += f"{progress['step']}\n\n"

        # Add Details section
        content += "## Details\n"
        if progress['details']:
            for detail in progress['details']:
                content += f"- {detail}\n"
        else:
            content += "- No specific details\n"
        content += "\n"

        # Add Notes section
        content += "## Notes\n"
        if progress['notes']:
            for note in progress['notes']:
                content += f"- {note}\n"
        else:
            content += "- No additional notes\n"

        try:
            with open(self.progress_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise Exception(f"Error writing progress file {self.progress_file_path}: {str(e)}")

    def get_current_step(self) -> str:
        """Returns the current step from progress.md."""
        progress = self.load_progress()
        return progress["step"]

    def advance_to_next_step(self, new_step: str, details: list = None, notes: list = None):
        """Advances to the next step and updates progress.md."""
        self.update_progress(step=new_step, details=details, notes=notes)

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
        step="B: Refinement, step 2",
        details=["Adjusting e2e test according to plan", "Implementing new features"],
        notes=["Previous step completed successfully", "Ready for implementation phase"]
    )

    print("Updated step:", pm.get_current_step())
