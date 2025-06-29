# progress_test.py
import os
import tempfile
import shutil
import json
from reb00t.helix.progress_manager import ProgressManager

def test_progress_manager():
    """Test the ProgressManager functionality."""
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    test_progress_file = os.path.join(test_dir, "progress.json")

    try:
        # Test 1: Initialize ProgressManager with custom path
        pm = ProgressManager(test_progress_file)

        # Test 2: Load progress from non-existent file (should return defaults)
        progress = pm.load_progress()
        assert progress["step"] == "A: Preparation, step 1"
        assert progress["details"] == []
        assert progress["notes"] == []
        assert progress["task"] == ""
        print("✅ Test 1 passed: Default progress loaded correctly")

        # Test 3: Update progress and verify file creation
        pm.update_progress(
            task="tasks/001-hello-world.json",
            step="B: Refinement, step 1",
            details=["Planning next refinement", "Awaiting user feedback"],
            notes=["E2E test framework working", "Ready for refinement loop"]
        )

        assert os.path.exists(test_progress_file), "Progress file should be created"
        print("✅ Test 2 passed: Progress file created successfully")

        # Test 4: Load progress from existing file
        progress = pm.load_progress()
        assert progress["step"] == "B: Refinement, step 1"
        assert progress["task"] == "tasks/001-hello-world.json"
        assert len(progress["details"]) == 2
        assert "Planning next refinement" in progress["details"]
        assert len(progress["notes"]) == 2
        assert "E2E test framework working" in progress["notes"]
        print("✅ Test 3 passed: Progress loaded from file correctly")

        # Test 5: Test get_current_step method
        current_step = pm.get_current_step()
        assert current_step == "B: Refinement, step 1"
        print("✅ Test 4 passed: get_current_step works correctly")

        # Test 6: Test advance_to_next_step
        pm.advance_to_next_step(
            "B: Refinement, step 2",
            details=["Adjusting e2e test according to plan"],
            notes=["Previous step completed successfully"]
        )

        progress = pm.load_progress()
        assert progress["step"] == "B: Refinement, step 2"
        assert progress["details"] == ["Adjusting e2e test according to plan"]
        assert progress["notes"] == ["Previous step completed successfully"]
        print("✅ Test 5 passed: advance_to_next_step works correctly")

        # Test 7: Test add_note method
        pm.add_note("New note added")
        progress = pm.load_progress()
        assert "New note added" in progress["notes"]
        assert len(progress["notes"]) == 2
        print("✅ Test 6 passed: add_note works correctly")

        # Test 8: Test add_detail method
        pm.add_detail("New detail added")
        progress = pm.load_progress()
        assert "New detail added" in progress["details"]
        assert len(progress["details"]) == 2
        print("✅ Test 7 passed: add_detail works correctly")

        # Test 9: Test partial updates (only updating one field)
        pm.update_progress(step="B: Refinement, step 3")
        progress = pm.load_progress()
        assert progress["step"] == "B: Refinement, step 3"
        # Details and notes should remain unchanged
        assert len(progress["details"]) == 2
        assert len(progress["notes"]) == 2
        print("✅ Test 8 passed: Partial update works correctly")

        # Test 9: Test task setting and retrieval
        pm.set_task("tasks/002-complex-task.json")
        progress = pm.load_progress()
        assert progress["task"] == "tasks/002-complex-task.json"
        assert pm.get_current_task() == "tasks/002-complex-task.json"
        print("✅ Test 8 passed: Task setting and retrieval works correctly")

        # Test 10: Verify file content format (JSON)
        with open(test_progress_file, 'r') as f:
            file_content = json.load(f)

        assert file_content["step"] == "B: Refinement, step 3"
        assert file_content["task"] == "tasks/002-complex-task.json"
        assert isinstance(file_content["details"], list)
        assert isinstance(file_content["notes"], list)
        assert len(file_content["details"]) == 2
        assert len(file_content["notes"]) == 2
        print("✅ Test 9 passed: JSON file format is correct")

        print("\n🎉 All tests passed! ProgressManager is working correctly.")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

    finally:
        # Clean up temporary directory
        shutil.rmtree(test_dir)


def test_progress_parser():
    """Test the progress file parser with JSON format."""
    test_dir = tempfile.mkdtemp()
    test_progress_file = os.path.join(test_dir, "progress.json")

    try:
        # Create a test progress file with specific JSON content
        test_data = {
            "task": "tasks/example-task.json",
            "step": "B: Refinement, step 1",
            "details": [
                "Planning next refinement",
                "Awaiting user feedback/adjustment for implementation direction"
            ],
            "notes": [
                "E2E test framework is in place and working",
                "AgenticSystem class successfully loads spec from test_data/spec.md",
                "Ready to begin refinement loop according to workflow specification"
            ]
        }

        with open(test_progress_file, 'w') as f:
            json.dump(test_data, f, indent=2)

        pm = ProgressManager(test_progress_file)
        progress = pm.load_progress()

        assert progress["step"] == "B: Refinement, step 1"
        assert progress["task"] == "tasks/example-task.json"
        assert len(progress["details"]) == 2
        assert "Planning next refinement" in progress["details"]
        assert "Awaiting user feedback/adjustment for implementation direction" in progress["details"]
        assert len(progress["notes"]) == 3
        assert "E2E test framework is in place and working" in progress["notes"]

        print("✅ Parser test passed: Complex JSON progress file parsed correctly")

    finally:
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_progress_manager()
    test_progress_parser()
    print("\n✅ All progress tests completed successfully!")
