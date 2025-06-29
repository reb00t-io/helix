# progress_test.py
import os
import tempfile
import shutil
from reb00t.helix.progress import ProgressManager

def test_progress_manager():
    """Test the ProgressManager functionality."""
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    test_progress_file = os.path.join(test_dir, "progress.md")
    
    try:
        # Test 1: Initialize ProgressManager with custom path
        pm = ProgressManager(test_progress_file)
        
        # Test 2: Load progress from non-existent file (should return defaults)
        progress = pm.load_progress()
        assert progress["step"] == "A: Preparation, step 1"
        assert progress["details"] == []
        assert progress["notes"] == []
        print("✅ Test 1 passed: Default progress loaded correctly")
        
        # Test 3: Update progress and verify file creation
        pm.update_progress(
            step="B: Refinement, step 1",
            details=["Planning next refinement", "Awaiting user feedback"],
            notes=["E2E test framework working", "Ready for refinement loop"]
        )
        
        assert os.path.exists(test_progress_file), "Progress file should be created"
        print("✅ Test 2 passed: Progress file created successfully")
        
        # Test 4: Load progress from existing file
        progress = pm.load_progress()
        assert progress["step"] == "B: Refinement, step 1"
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
        
        # Test 10: Verify file content format
        with open(test_progress_file, 'r') as f:
            content = f.read()
        
        assert "# Progress" in content
        assert "## Step" in content
        assert "## Details" in content
        assert "## Notes" in content
        assert "B: Refinement, step 3" in content
        print("✅ Test 9 passed: File format is correct")
        
        print("\n🎉 All tests passed! ProgressManager is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(test_dir)


def test_progress_parser():
    """Test the progress file parser with various formats."""
    test_dir = tempfile.mkdtemp()
    test_progress_file = os.path.join(test_dir, "progress.md")
    
    try:
        # Create a test progress file with specific content
        test_content = """# Progress

## Step
B: Refinement, step 1

## Details
- Planning next refinement
- Awaiting user feedback/adjustment for implementation direction

## Notes
- E2E test framework is in place and working
- AgenticSystem class successfully loads spec from test_data/spec.md
- Ready to begin refinement loop according to workflow specification
"""
        
        with open(test_progress_file, 'w') as f:
            f.write(test_content)
        
        pm = ProgressManager(test_progress_file)
        progress = pm.load_progress()
        
        assert progress["step"] == "B: Refinement, step 1"
        assert len(progress["details"]) == 2
        assert "Planning next refinement" in progress["details"]
        assert "Awaiting user feedback/adjustment for implementation direction" in progress["details"]
        assert len(progress["notes"]) == 3
        assert "E2E test framework is in place and working" in progress["notes"]
        
        print("✅ Parser test passed: Complex progress file parsed correctly")
        
    finally:
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_progress_manager()
    test_progress_parser()
    print("\n✅ All progress tests completed successfully!")
