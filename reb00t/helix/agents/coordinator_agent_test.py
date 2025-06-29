# agent_test.py
import tempfile
import shutil
import os
from reb00t.helix.agents.coordinator_agent import CoordinatorAgent
from reb00t.helix.progress import ProgressManager

def test_refinement_agent():
    """Test the RefinementAgent functionality."""
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()

    try:
        os.chdir(test_dir)

        # Create test spec.md file
        with open("spec.md", "w") as f:
            f.write("""# Test Spec
## Purpose
Test specification for agent testing
## Core Components
1. **Test Component** - For testing purposes
""")

        # Create test progress.md file
        with open("progress.md", "w") as f:
            f.write("""# Progress
## Step
B: Refinement, step 1
## Details
- Initial test setup
## Notes
- Testing agent functionality
""")

        # Test 1: Initialize agent
        agent = CoordinatorAgent(ProgressManager())
        assert agent is not None
        print("✅ Test 1 passed: Agent initialized successfully")

        # Test 2: Run refinement cycle
        spec = None
        result = agent.run_refinement_cycle(spec)
        assert result is not None
        assert "cycle_completed" in result
        assert "steps_completed" in result
        print("✅ Test 2 passed: Refinement cycle executed")

        # Test 3: Verify steps were completed
        expected_steps = ['plan', 'adjust_test', 'implement', 'test_check', 'spec_review', 'commit']
        assert all(step in result['steps_completed'] for step in expected_steps)
        print("✅ Test 3 passed: All expected steps completed")

        # Test 4: Test user feedback functionality
        spec = None
        agent._plan_next_refinement(spec)  # Generate a plan
        feedback = {"approved": True}
        feedback_result = agent.accept_user_feedback(feedback)
        assert feedback_result["status"] == "approved"
        print("✅ Test 4 passed: User feedback processing works")

        # Test 5: Test plan modification
        spec = None
        agent._plan_next_refinement(spec)  # Generate a plan
        modification_feedback = {
            "modifications": {
                "summary": "Modified test plan"
            }
        }
        mod_result = agent.accept_user_feedback(modification_feedback)
        assert mod_result["status"] == "modified"
        assert agent.current_plan["summary"] == "Modified test plan"
        print("✅ Test 5 passed: Plan modification works")

        # Test 6: Verify progress updates
        assert os.path.exists("progress.md")
        with open("progress.md", "r") as f:
            progress_content = f.read()
        assert "Refinement cycle completed successfully" in progress_content
        print("✅ Test 6 passed: Progress file updated correctly")

        print("\n🎉 All agent tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

    finally:
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)


def test_agent_error_handling():
    """Test agent error handling."""
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()

    try:
        os.chdir(test_dir)

        # Don't create spec.md to test error handling
        agent = CoordinatorAgent(ProgressManager())

        # This should handle the missing spec file gracefully
        spec = None
        result = agent.run_refinement_cycle(spec)

        # Should have errors but not crash
        assert "errors" in result
        print("✅ Error handling test passed: Agent handles missing files gracefully")

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        raise

    finally:
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_refinement_agent()
    test_agent_error_handling()
    print("\n✅ All agent tests completed successfully!")
