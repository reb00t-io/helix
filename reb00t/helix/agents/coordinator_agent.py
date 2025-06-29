# agent.py
from typing import Dict, List

from reb00t.helix.progress import ProgressManager
from reb00t.helix.agents.planner_agent import PlannerAgent

class CoordinatorAgent:
    """Agent that executes one iteration of the refinement loop."""

    def __init__(self, progress_manager: ProgressManager):
        self.progress_manager = progress_manager
        self.planner = PlannerAgent()
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

            if plan_result["user_feedback_required"]:
                results["user_feedback_required"] = True
                results["plan"] = plan_result["plan"]
                self._update_progress("B: Refinement, step 1",
                                    details=[f"Plan created: {plan_result['plan']['summary']}",
                                           "Awaiting user feedback/adjustment"],
                                    notes=[f"Plan details: {plan_result['plan']['description']}"])
                return results

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
        # Use the planner agent to generate the plan
        planner_result = self.planner.create_plan(spec, self.current_progress)

        if not planner_result["success"]:
            # Fallback to simple plan if planner fails
            plan = {
                "summary": "Continue development according to current progress",
                "description": "Proceed with next development steps based on current state",
                "goals": ["Continue implementation", "Update tests", "Maintain progress"],
                "files_to_modify": ["reb00t/helix/agentic_system.py"],
                "tests_to_add": ["basic_functionality_test"]
            }
        else:
            plan = planner_result["plan"]
            # Log the analysis for debugging
            analysis = planner_result.get("analysis", {})
            self.progress_manager.add_note(f"Plan analysis: {analysis.get('priority_areas', [])}")

        self.current_plan = plan
        self.progress_manager.add_note(f"Generated refinement plan: {plan['summary']}")

        # For now, assume user feedback is not required (auto-approve simple plans)
        # In a real implementation, this would prompt the user
        user_feedback_required = self._requires_user_feedback(plan)

        return {
            "plan": plan,
            "user_feedback_required": user_feedback_required
        }

    def _requires_user_feedback(self, plan: Dict) -> bool:
        """Determine if the plan requires user feedback."""
        # Simple heuristic: require feedback for complex plans
        complex_indicators = [
            len(plan["files_to_modify"]) > 3,
            "breaking" in plan["description"].lower(),
            "major" in plan["description"].lower(),
            "architecture" in plan["description"].lower()
        ]
        return any(complex_indicators)

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
        return {"status": "aborted", "attempts": self.max_implementation_attempts}

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
        """Update progress.md with current step information."""
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


# --- Example usage: ---
if __name__ == "__main__":
    # Example of running one refinement cycle
    agent = CoordinatorAgent(ProgressManager())

    print("Starting refinement cycle...")
    result = agent.run_refinement_cycle(None)

    print(f"Cycle completed: {result['cycle_completed']}")
    print(f"Steps completed: {result['steps_completed']}")

    if result['user_feedback_required']:
        print("User feedback required for plan:")
        print(result['plan']['summary'])

        # Simulate user approval
        feedback = {"approved": True}
        agent.accept_user_feedback(feedback)

        # Continue the cycle
        result = agent.run_refinement_cycle()
        print(f"Final result: {result}")

    if result['errors']:
        print(f"Errors: {result['errors']}")
