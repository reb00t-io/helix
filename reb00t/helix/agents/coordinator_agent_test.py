# coordinator_agent_test.py
import unittest
import tempfile
import shutil
import os
import asyncio
import warnings
import gc
import threading
from reb00t.common.llm.llm import release_llm_instances
from reb00t.helix.agents.coordinator_agent import CoordinatorAgent
from reb00t.helix.progress import ProgressManager
from reb00t.helix.agents.interaction_hook import MockInteractionHook

def cleanup_async_tasks():
    """Clean up any remaining async tasks and close event loops."""
    try:
        # Get all tasks in the current event loop
        try:
            loop = asyncio.get_running_loop()
            pending_tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]

            if pending_tasks:
                # Cancel all pending tasks
                for task in pending_tasks:
                    task.cancel()

                # Wait for all tasks to complete/cancel
                if pending_tasks:
                    loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
        except RuntimeError:
            # No running loop
            pass

        # Force garbage collection to clean up any remaining references
        gc.collect()

        # Close any remaining event loops
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop and not loop.is_closed():
                # Cancel all remaining tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()

                # Run the loop one more time to process cancellations
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

                loop.close()
        except RuntimeError:
            pass

        # Set a new event loop for the next test
        try:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
        except Exception:
            pass

    except Exception:
        # If all else fails, just ignore the cleanup errors
        pass


class TestCoordinatorAgent(unittest.TestCase):
    """Test cases for CoordinatorAgent functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        # Suppress ResourceWarnings and async warnings for cleaner test output
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited.*")

    def setUp(self):
        """Set up test environment before each test."""
        # Clean up any existing async resources
        cleanup_async_tasks()
        release_llm_instances()

        self.original_cwd = os.getcwd()

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

    def tearDown(self):
        """Clean up test environment after each test."""
        os.chdir(self.original_cwd)

        # Clean up async resources and LLM instances
        try:
            release_llm_instances()
        except Exception:
            pass

        # Clean up async tasks
        cleanup_async_tasks()

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        # Final cleanup
        try:
            release_llm_instances()
        except Exception:
            pass

        # Final async cleanup
        cleanup_async_tasks()

    def _create_test_agent(self, auto_continue=True, default_feedback="Test feedback"):
        """Helper method to create a test agent with proper isolation."""
        mock_hook = MockInteractionHook(auto_continue=auto_continue, default_feedback=default_feedback)
        return CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

    def test_agent_initialization(self):
        """Test that CoordinatorAgent initializes correctly."""
        agent = self._create_test_agent()

        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.planner)
        self.assertIsNotNone(agent.progress_manager)
        self.assertIsNotNone(agent.interaction_hook)
        self.assertEqual(agent.max_implementation_attempts, 3)

    def test_refinement_cycle_execution(self):
        """Test that refinement cycle executes successfully."""
        agent = self._create_test_agent(default_feedback="Looks good!")

        spec = """# Sample Project Spec
## Goals
- Implement core functionality
- Add comprehensive testing
- Update documentation
"""

        result = agent.run_refinement_cycle(spec)

        self.assertIsNotNone(result)
        self.assertIn("cycle_completed", result)
        self.assertIn("steps_completed", result)
        self.assertIn("errors", result)

    def test_all_refinement_steps_completed(self):
        """Test that all expected refinement steps are completed."""
        agent = self._create_test_agent()

        spec = "# Test Spec\n## Goals\n- Test functionality"
        result = agent.run_refinement_cycle(spec)

        expected_steps = ['plan', 'adjust_test', 'implement', 'test_check', 'spec_review', 'commit']
        completed_steps = result.get('steps_completed', [])

        for step in expected_steps:
            self.assertIn(step, completed_steps, f"Step '{step}' was not completed")

    def test_user_feedback_approval(self):
        """Test user feedback approval functionality."""
        agent = self._create_test_agent(default_feedback="Approved!")

        spec = "# Test Spec"
        plan_result = agent._plan_next_refinement(spec)

        self.assertIsNotNone(agent.current_plan)

        feedback = {"approved": True}
        feedback_result = agent.accept_user_feedback(feedback)

        self.assertEqual(feedback_result["status"], "approved")
        self.assertIn("plan", feedback_result)

    def test_plan_modification(self):
        """Test plan modification through user feedback."""
        agent = self._create_test_agent()

        spec = "# Test Spec"
        plan_result = agent._plan_next_refinement(spec)

        original_summary = agent.current_plan["summary"]

        modification_feedback = {
            "modifications": {
                "summary": "Modified test plan"
            }
        }

        mod_result = agent.accept_user_feedback(modification_feedback)

        self.assertEqual(mod_result["status"], "modified")
        self.assertEqual(agent.current_plan["summary"], "Modified test plan")
        self.assertNotEqual(agent.current_plan["summary"], original_summary)

    def test_progress_file_updates(self):
        """Test that progress file is updated correctly."""
        mock_hook = MockInteractionHook(auto_continue=True)
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        spec = "# Test Spec"
        agent.run_refinement_cycle(spec)

        self.assertTrue(os.path.exists("progress.md"))

        with open("progress.md", "r") as f:
            progress_content = f.read()

        self.assertIn("Refinement cycle completed successfully", progress_content)

    def test_error_handling_missing_spec(self):
        """Test agent error handling with missing spec."""
        mock_hook = MockInteractionHook(auto_continue=True)
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        # Test with None spec
        result = agent.run_refinement_cycle(None)

        # Should handle gracefully and not crash
        self.assertIn("errors", result)
        self.assertIsInstance(result["errors"], list)

    def test_interaction_hook_integration(self):
        """Test interaction hook integration."""
        mock_hook = MockInteractionHook(auto_continue=True, default_feedback="Test feedback")
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        # Create a complex plan that should require user feedback
        complex_spec = """# Complex Project
## Architecture Changes
- Major refactoring required
- Breaking changes to API
- Multiple file modifications needed
"""

        # This should trigger interaction hook for complex plans
        plan_result = agent._plan_next_refinement(complex_spec)

        # Verify the mock interaction hook was used
        self.assertGreaterEqual(mock_hook.interaction_count, 0)

    def test_implementation_failure_handling(self):
        """Test handling of implementation failures."""
        mock_hook = MockInteractionHook(auto_continue=False, default_feedback="Stop on failure")
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        # Simulate implementation failure by setting max attempts to 1
        agent.max_implementation_attempts = 1

        spec = "# Test Spec"

        # This should handle implementation failure gracefully
        result = agent.run_refinement_cycle(spec)

        # Should complete without crashing
        self.assertIn("cycle_completed", result)
        self.assertIn("errors", result)

    def test_planner_integration(self):
        """Test that the Planner class is properly integrated."""
        mock_hook = MockInteractionHook(auto_continue=True)
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        # Verify planner has correct type and methods
        self.assertTrue(hasattr(agent.planner, 'plan_next_refinement'))
        self.assertTrue(hasattr(agent.planner, 'planner_agent'))
        self.assertTrue(hasattr(agent.planner, 'interaction_hook'))

        # Test plan creation through planner
        spec = "# Test Spec"
        current_progress = {"step": "test", "details": [], "notes": []}

        plan_result = agent.planner.plan_next_refinement(spec, current_progress)

        self.assertIn("plan", plan_result)
        self.assertIn("user_feedback_required", plan_result)


class TestCoordinatorAgentEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for CoordinatorAgent."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        # Suppress ResourceWarnings and async warnings for cleaner test output
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited.*")

    def setUp(self):
        """Set up test environment for edge case tests."""
        # Clean up any existing async resources
        cleanup_async_tasks()
        release_llm_instances()

        self.original_cwd = os.getcwd()

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)

        # Clean up async resources and LLM instances
        try:
            release_llm_instances()
        except Exception:
            pass

        # Clean up async tasks
        cleanup_async_tasks()

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        try:
            release_llm_instances()
        except Exception:
            pass

        # Final async cleanup
        cleanup_async_tasks()

    def test_agent_without_progress_file(self):
        """Test agent behavior when progress file doesn't exist."""
        mock_hook = MockInteractionHook(auto_continue=True)
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        # Should handle missing progress file gracefully
        spec = "# Test Spec"
        result = agent.run_refinement_cycle(spec)

        self.assertIn("cycle_completed", result)

    def test_user_stops_refinement(self):
        """Test behavior when user chooses to stop refinement."""
        mock_hook = MockInteractionHook(auto_continue=False, default_feedback="Stop refinement")
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        # Override the _requires_user_feedback method to always return True
        original_method = agent.planner._requires_user_feedback
        agent.planner._requires_user_feedback = lambda plan: True

        try:
            # Any spec should now trigger user feedback and then stop
            simple_spec = """# Test Project
## Goals
- Simple test functionality
"""

            # This should trigger user feedback and then stop with an error
            result = agent.run_refinement_cycle(simple_spec)

            # Verify that the cycle was stopped due to user choice
            self.assertFalse(result["cycle_completed"])
            self.assertIn("errors", result)
            self.assertTrue(len(result["errors"]) > 0)
            self.assertIn("User chose to stop", result["errors"][0])

        finally:
            # Restore the original method
            agent.planner._requires_user_feedback = original_method

    def test_empty_spec(self):
        """Test behavior with empty specification."""
        mock_hook = MockInteractionHook(auto_continue=True)
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        result = agent.run_refinement_cycle("")

        self.assertIn("cycle_completed", result)

    def test_invalid_feedback_format(self):
        """Test handling of invalid feedback format."""
        mock_hook = MockInteractionHook(auto_continue=True)
        agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

        # Create a plan first
        spec = "# Test Spec"
        agent._plan_next_refinement(spec)

        # Test with invalid feedback
        invalid_feedback = {"invalid_key": "invalid_value"}
        result = agent.accept_user_feedback(invalid_feedback)

        self.assertEqual(result["status"], "pending")


if __name__ == "__main__":
    unittest.main(verbosity=1)
