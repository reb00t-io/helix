# agent.py
from typing import Dict, List, Any

try:
    from reb00t.helix.progress_manager import ProgressManager
    from reb00t.helix.agents.planner import Planner
    from reb00t.helix.agents.interaction_hook import InteractionHook, CLIInteractionHook
except ImportError:
    # For standalone execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from reb00t.helix.progress_manager import ProgressManager
    from reb00t.helix.agents.planner import Planner
    from agents.interaction_hook import InteractionHook, CLIInteractionHook

class CoordinatorAgent:
    """Agent that executes one iteration of the refinement loop."""

    def __init__(self, progress_manager: ProgressManager, interaction_hook: InteractionHook = None):
        self.progress_manager = progress_manager
        self.interaction_hook = interaction_hook or CLIInteractionHook()
        self.planner = Planner(self.interaction_hook, self.progress_manager)
        self.current_progress = None
        self.current_plan = None
        self.test_results = []
        self.implementation_attempts = 0
        self.max_implementation_attempts = 3

    def run_refinement_cycle(self, spec) -> Dict:
        """Executes one complete refinement cycle according to the spec."""
        results = {
            "cycle_completed": False,
            "steps_completed": [],
            "errors": [],
            "user_feedback_required": False,
            "spec_changed": False,
            "committed": False
        }

        self.current_progress = self.progress_manager.load_progress()

        try:
            # Step 1: Plan next refinement
            plan_result = self._plan_next_refinement(spec)
            results["steps_completed"].append("plan")

            # Step 2: Adjust e2e test according to plan
            test_result = self._adjust_e2e_test(plan_result["plan"])
            results["steps_completed"].append("adjust_test")

            # Step 3: Implement refinement including unit tests
            impl_result = self._implement_refinement(plan_result["plan"])
            results["steps_completed"].append("implement")

            # Step 4: Check e2e test and fix if needed
            test_check_result = self._check_and_fix_tests()
            results["steps_completed"].append("test_check")

            if test_check_result["status"] == "aborted":
                results["errors"].append("Implementation failed after multiple attempts")
                self._update_progress("B: Refinement, step 4",
                                    details=["Implementation aborted", "Plan needs to change"],
                                    notes=["Multiple implementation attempts failed"])
                return results

            # Step 5: Review spec and make changes if needed
            spec_result = self._review_and_update_spec()
            results["steps_completed"].append("spec_review")
            results["spec_changed"] = spec_result["changed"]

            # Step 6: Commit changes
            commit_result = self._commit_changes(plan_result["plan"])
            results["steps_completed"].append("commit")
            results["committed"] = commit_result["success"]

            # Step 7: Determine if cycle should continue
            continue_result = self._should_continue()
            results["should_continue"] = continue_result["continue"]
            results["completion_reason"] = continue_result["reason"]

            results["cycle_completed"] = True
            self._update_progress("B: Refinement, step 7",
                                details=["Refinement cycle completed successfully"],
                                notes=[f"Completed plan: {plan_result['plan']['summary']}"])

        except Exception as e:
            results["errors"].append(f"Refinement cycle failed: {str(e)}")

        return results

    def _plan_next_refinement(self, spec) -> Dict:
        """Step 1: Plan next refinement and ask for user feedback."""
        # Use the planner to generate the plan and handle user feedback
        plan_result = self.planner.plan_next_refinement(spec, self.current_progress)

        # Store the current plan for later use
        self.current_plan = plan_result["plan"]

        return plan_result

    def _adjust_e2e_test(self, plan: Dict) -> Dict:
        """Step 2: Adjust e2e test according to plan."""
        test_adjustments = []

        # Analyze what test changes are needed based on the plan
        if "progress integration" in plan["description"].lower():
            test_adjustments.append("Add progress functionality tests")
            test_adjustments.append("Verify progress events in history")
            test_adjustments.append("Test progress note addition")

        self.progress_manager.add_note(f"E2E test adjustments planned: {', '.join(test_adjustments)}")

        return {
            "adjustments": test_adjustments,
            "files_modified": plan.get("files_to_modify", [])
        }

    def _implement_refinement(self, plan: Dict) -> Dict:
        """Step 3: Implement refinement including unit tests."""
        implementation_results = []

        # Simulate implementation steps
        for goal in plan["goals"]:
            implementation_results.append(f"Implemented: {goal}")

        # Add unit tests
        unit_tests = plan.get("tests_to_add", [])
        for test in unit_tests:
            implementation_results.append(f"Added unit test: {test}")

        self.progress_manager.add_note(f"Implementation completed: {len(implementation_results)} items")

        return {
            "implemented": implementation_results,
            "unit_tests_added": unit_tests
        }

    def _check_and_fix_tests(self) -> Dict:
        """Step 4: Check e2e test and fix implementation if needed."""
        for attempt in range(self.max_implementation_attempts):
            test_result = self._run_e2e_tests()

            if test_result["passed"]:
                self.progress_manager.add_note(f"E2E tests passed on attempt {attempt + 1}")
                return {"status": "passed", "attempts": attempt + 1}

            if attempt < self.max_implementation_attempts - 1:
                # Try to fix the implementation
                fix_result = self._fix_implementation(test_result["errors"])
                self.progress_manager.add_note(f"Attempt {attempt + 1} failed, applying fix: {fix_result['fix_description']}")
            else:
                # Consider adjusting e2e test if implementation consistently fails
                adjustment_result = self._consider_test_adjustment(test_result["errors"])
                if adjustment_result["adjusted"]:
                    self.progress_manager.add_note(f"Adjusted e2e test: {adjustment_result['reason']}")
                    return {"status": "test_adjusted", "attempts": attempt + 1}

        # If we get here, implementation failed multiple times
        self.progress_manager.add_note("Implementation failed after maximum attempts")

        # Ask user for guidance on how to proceed
        user_decision = self._handle_implementation_failure()

        if user_decision["action"] == "stop":
            return {"status": "aborted", "attempts": self.max_implementation_attempts, "reason": user_decision["reason"]}
        elif user_decision["action"] == "continue":
            self.progress_manager.add_note(f"User chose to continue despite failures: {user_decision['guidance']}")
            return {"status": "continued_with_failures", "attempts": self.max_implementation_attempts}

        # For other actions, we'll still return aborted but with the user's guidance
        self.progress_manager.add_note(f"User guidance for next iteration: {user_decision['guidance']}")
        return {"status": "aborted", "attempts": self.max_implementation_attempts, "user_guidance": user_decision["guidance"]}

    def _run_e2e_tests(self) -> Dict:
        """Run the e2e tests and return results."""
        # In a real implementation, this would run actual tests
        # For now, simulate test execution
        try:
            # Simulate running the test
            # In practice, this would execute: python run_test.py
            self.test_results.append("e2e_test_run")

            # Simulate success (for this example)
            return {
                "passed": True,
                "errors": [],
                "output": "All tests passed"
            }
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "output": f"Test failed: {str(e)}"
            }

    def _fix_implementation(self, errors: List[str]) -> Dict:
        """Attempt to fix implementation based on test errors."""
        # Analyze errors and apply fixes
        fix_description = f"Applied fixes for {len(errors)} errors"

        # In a real implementation, this would analyze error messages
        # and apply specific fixes

        return {
            "fix_applied": True,
            "fix_description": fix_description,
            "errors_addressed": len(errors)
        }

    def _consider_test_adjustment(self, errors: List[str]) -> Dict:
        """Consider adjusting the e2e test if implementation consistently fails."""
        # Analyze if the test expectations are unrealistic
        adjustment_needed = len(errors) > 2  # Simple heuristic

        if adjustment_needed:
            return {
                "adjusted": True,
                "reason": "Test expectations were too strict for current implementation"
            }

        return {"adjusted": False, "reason": "Test adjustment not needed"}

    def _review_and_update_spec(self) -> Dict:
        """Step 5: Review spec and update if needed."""
        # Analyze if spec changes are needed based on implementation
        spec_analysis = self._analyze_spec_changes_needed()

        if spec_analysis["changes_needed"]:
            # Apply spec changes
            changes = self._apply_spec_changes(spec_analysis["changes"])
            self.progress_manager.add_note(f"Updated spec: {changes['summary']}")
            return {"changed": True, "changes": changes}
        else:
            self.progress_manager.add_note("No spec changes needed")
            return {"changed": False, "changes": None}

    def _analyze_spec_changes_needed(self) -> Dict:
        """Analyze if spec changes are needed."""
        # Simple heuristic: if we added new major functionality, update spec
        if self.current_plan and "progress integration" in self.current_plan["description"].lower():
            return {
                "changes_needed": True,
                "changes": [
                    "Add ProgressManager integration to AgenticSystem documentation",
                    "Update workflow to include progress tracking"
                ]
            }

        return {"changes_needed": False, "changes": []}

    def _apply_spec_changes(self, changes: List[str]) -> Dict:
        """Apply changes to the spec."""
        # In a real implementation, this would modify the spec.md file
        return {
            "summary": f"Applied {len(changes)} spec changes",
            "changes_applied": changes
        }

    def _commit_changes(self, plan: Dict) -> Dict:
        """Step 6: Commit changes."""
        try:
            # In a real implementation, this would use git
            commit_message = f"feat: {plan['summary']}\n\n{plan['description']}"

            # Simulate git operations
            self.progress_manager.add_note(f"Committed changes: {plan['summary']}")

            return {
                "success": True,
                "commit_message": commit_message,
                "files_committed": plan.get("files_to_modify", [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _should_continue(self) -> Dict:
        """Step 7: Determine if refinement should continue."""

        # Check if we've reached a completion milestone
        completion_indicators = [
            "all tests passing",
            "implementation complete",
            "spec updated"
        ]

        # For this example, assume we should continue unless explicitly done
        continue_refinement = True
        reason = "More refinements available"

        # In a real implementation, this would analyze project state
        # and determine if the project goals are met

        return {
            "continue": continue_refinement,
            "reason": reason
        }

    def _update_progress(self, step: str, details: List[str] = None, notes: List[str] = None):
        """Update progress.json with current step information."""
        self.progress_manager.update_progress(
            step=step,
            details=details or [],
            notes=notes or []
        )

    def accept_user_feedback(self, feedback: Dict) -> Dict:
        """Process user feedback on the refinement plan."""
        if not self.current_plan:
            return {"error": "No current plan to provide feedback on"}

        # Apply user feedback to the plan
        if "approved" in feedback and feedback["approved"]:
            self.progress_manager.add_note("User approved refinement plan")
            return {"status": "approved", "plan": self.current_plan}

        if "modifications" in feedback:
            # Apply user modifications to the plan
            for key, value in feedback["modifications"].items():
                if key in self.current_plan:
                    self.current_plan[key] = value

            self.progress_manager.add_note(f"Applied user modifications to plan")
            return {"status": "modified", "plan": self.current_plan}

        return {"status": "pending", "plan": self.current_plan}

    def _request_user_decision(self, title: str, message: str, context: Dict = None) -> Dict[str, Any]:
        """
        Request a decision from the user at a critical point in the refinement cycle.

        Args:
            title: Title for the decision request
            message: Message explaining what decision is needed
            context: Additional context information

        Returns:
            Dictionary containing user feedback with 'text' and 'continue' keys
        """
        feedback_context = {
            "title": title,
            "message": message
        }

        if context:
            feedback_context.update(context)

        return self.interaction_hook.request_user_feedback(feedback_context)

    def _handle_implementation_failure(self) -> Dict:
        """
        Handle the case where implementation fails multiple times and ask user for guidance.
        """
        feedback_context = {
            "title": "Implementation Failure",
            "message": f"Implementation has failed {self.max_implementation_attempts} times. " +
                      "What would you like to do?",
            "options": [
                "1. Try a different approach",
                "2. Simplify the plan",
                "3. Stop refinement",
                "4. Continue anyway"
            ]
        }

        user_decision = self.interaction_hook.request_user_feedback(feedback_context)

        if not user_decision["continue"]:
            return {"action": "stop", "reason": "User chose to stop after implementation failure"}

        # Parse user guidance
        feedback_text = user_decision["text"].lower()
        if "different" in feedback_text or "approach" in feedback_text:
            return {"action": "retry_different", "guidance": user_decision["text"]}
        elif "simplify" in feedback_text:
            return {"action": "simplify", "guidance": user_decision["text"]}
        elif "continue" in feedback_text or "anyway" in feedback_text:
            return {"action": "continue", "guidance": user_decision["text"]}
        else:
            return {"action": "retry", "guidance": user_decision["text"]}


# --- Example usage: ---
if __name__ == "__main__":
    try:
        from reb00t.helix.agents.interaction_hook import MockInteractionHook
    except ImportError:
        from agents.interaction_hook import MockInteractionHook

    # Example of running one refinement cycle with mock interaction hook
    mock_hook = MockInteractionHook(auto_continue=True, default_feedback="Looks good!")
    agent = CoordinatorAgent(ProgressManager(), interaction_hook=mock_hook)

    print("Starting refinement cycle...")

    # Sample spec for testing
    sample_spec = """
    # Sample Project Spec
    ## Goals
    - Implement core functionality
    - Add comprehensive testing
    - Update documentation
    """

    result = agent.run_refinement_cycle(sample_spec)

    print(f"Cycle completed: {result['cycle_completed']}")
    print(f"Steps completed: {result['steps_completed']}")

    if result['errors']:
        print(f"Errors: {result['errors']}")

    print(f"Mock interactions: {mock_hook.interaction_count}")

    # Example with CLI interaction hook (uncomment to test interactively)
    # print("\n" + "="*50)
    # print("Testing with CLI interaction hook...")
    # cli_agent = CoordinatorAgent(ProgressManager())  # Uses CLIInteractionHook by default
    # cli_result = cli_agent.run_refinement_cycle(sample_spec)
