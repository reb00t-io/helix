# planner.py
from typing import Dict, List
from reb00t.helix.agents.planner_agent import PlannerAgent
from reb00t.helix.agents.interaction_hook import InteractionHook


class Planner:
    """High-level planner that orchestrates plan creation and user feedback."""

    def __init__(self, interaction_hook: InteractionHook, progress_manager):
        self.planner_agent = PlannerAgent()
        self.interaction_hook = interaction_hook
        self.progress_manager = progress_manager

    def plan_next_refinement(self, spec: str, current_progress: Dict) -> Dict:
        """Plan next refinement and handle user feedback if needed."""
        # Use the planner agent to generate the plan
        planner_result = self.planner_agent.create_plan(spec, current_progress)

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

        self.progress_manager.add_note(f"Generated refinement plan: {plan['summary']}")

        # Determine if user feedback is required
        user_feedback_required = self._requires_user_feedback(plan)

        if user_feedback_required:
            # Use interaction hook to get user feedback
            feedback_context = {
                "title": "Refinement Plan Review",
                "plan": plan,
                "message": "Please review the proposed refinement plan. Provide feedback or approve to continue."
            }

            user_feedback = self.interaction_hook.request_user_feedback(feedback_context)

            # Process the feedback
            if not user_feedback["continue"]:
                # User wants to stop
                self.progress_manager.update_progress(
                    step="B: Refinement, step 1",
                    details=["Plan created but user chose to stop"],
                    notes=[f"User feedback: {user_feedback['text']}"]
                )
                raise RuntimeError("User chose to stop refinement cycle")

            # Apply user feedback to the plan if provided
            if user_feedback["text"]:
                # Store the feedback and potentially modify the plan
                self.progress_manager.add_note(f"User feedback: {user_feedback['text']}")
                # For now, we'll proceed with the original plan
                # In a more sophisticated implementation, we could parse the feedback
                # and modify the plan accordingly

            # Continue with the approved plan
            self.progress_manager.add_note("User approved plan, continuing with refinement")

            # Update progress to reflect user approval
            self.progress_manager.update_progress(
                step="B: Refinement, step 1 (approved)",
                details=[f"Plan approved: {plan['summary']}", "Proceeding with implementation"],
                notes=[f"Plan details: {plan['description']}"]
            )

        return {
            "plan": plan,
            "user_feedback_required": user_feedback_required
        }

    def _requires_user_feedback(self, plan: Dict) -> bool:
        """Determine if the plan requires user feedback."""
        # Simple heuristic: require feedback for complex plans
        complex_indicators = [
            len(plan.get("files_to_modify", [])) > 3,
            "breaking" in plan.get("description", "").lower(),
            "major" in plan.get("description", "").lower(),
            "architecture" in plan.get("description", "").lower()
        ]
        return any(complex_indicators)

    def get_plan_history(self) -> List[Dict]:
        """Get the history of generated plans."""
        return self.planner_agent.get_plan_history()
