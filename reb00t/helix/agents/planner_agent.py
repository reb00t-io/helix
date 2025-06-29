# planner_agent.py
from typing import Dict, List
from reb00t.helix.agents.abstract_agent import AbstractAgent

class PlannerAgent(AbstractAgent):
    """Agent that creates refinement plans using LLM analysis of spec and progress."""

    def __init__(self, llm_client=None):
        super().__init__("planner", llm_client)
        self.plan_history = []

    def create_plan(self, spec: str, current_progress: Dict) -> Dict:
        """
        Creates a refinement plan based on the spec and current progress.

        Args:
            spec: The project specification content
            current_progress: Current progress data from progress.md

        Returns:
            Dict containing the generated plan
        """
        try:
            # Analyze the current state
            analysis = self._analyze_current_state(spec, current_progress)

            # Generate plan using LLM
            plan = self._generate_plan_with_llm(spec, current_progress, analysis)

            # Validate and enhance the plan
            validated_plan = self._validate_and_enhance_plan(plan)

            # Store in history
            self.plan_history.append(validated_plan)

            return {
                "success": True,
                "plan": validated_plan,
                "analysis": analysis
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "plan": None
            }

    def _analyze_current_state(self, spec: str, current_progress: Dict) -> Dict:
        """Analyze the current project state to inform planning."""
        analysis = {
            "current_step": current_progress.get("step", "Unknown"),
            "completed_items": [],
            "pending_items": [],
            "spec_requirements": [],
            "technical_debt": [],
            "priority_areas": []
        }

        # Extract key information from spec
        if "Core Components" in spec:
            analysis["spec_requirements"] = self._extract_spec_requirements(spec)

        # Analyze progress details and notes
        details = current_progress.get("details", [])
        notes = current_progress.get("notes", [])

        # Identify completed vs pending items
        for detail in details:
            if any(word in detail.lower() for word in ["complete", "done", "finished"]):
                analysis["completed_items"].append(detail)
            else:
                analysis["pending_items"].append(detail)

        # Extract technical insights from notes
        for note in notes:
            if any(word in note.lower() for word in ["error", "issue", "problem", "fix"]):
                analysis["technical_debt"].append(note)

        # Determine priority areas based on current step
        current_step = analysis["current_step"].lower()
        if "preparation" in current_step:
            analysis["priority_areas"] = ["spec_completion", "basic_structure", "testing_framework"]
        elif "refinement" in current_step:
            analysis["priority_areas"] = ["implementation", "testing", "integration"]

        return analysis

    def _extract_spec_requirements(self, spec: str) -> List[str]:
        """Extract key requirements from the spec."""
        requirements = []

        # Look for key sections
        sections = ["Core Components", "Workflow", "Invariants"]
        for section in sections:
            if section in spec:
                # Extract bullet points or numbered items
                section_start = spec.find(section)
                section_text = spec[section_start:section_start + 1000]  # Get reasonable chunk

                # Simple extraction of requirements
                lines = section_text.split('\n')
                for line in lines:
                    if line.strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.')):
                        requirement = line.strip().lstrip('-*123456789. ')
                        if len(requirement) > 10:  # Filter out very short items
                            requirements.append(requirement)

        return requirements[:10]  # Limit to top 10 most important

    def _generate_plan_with_llm(self, spec: str, current_progress: Dict, analysis: Dict) -> Dict:
        """Generate a plan using LLM analysis."""

        # Prepare the prompt for the LLM
        prompt = self._create_planning_prompt(spec, current_progress, analysis)

        # Use the base class generate method with JSON parsing and fallback
        return self.generate(prompt, parse_json=True).data

    def _create_planning_prompt(self, spec: str, current_progress: Dict, analysis: Dict) -> str:
        """Create a prompt for LLM-based planning."""
        prompt = f"""
You are an expert software development planner. Based on the provided specification and current progress, create a detailed refinement plan.

SPECIFICATION:
{spec[:2000]}...

CURRENT PROGRESS:
Step: {current_progress.get('step', 'Unknown')}
Details: {current_progress.get('details', [])}
Notes: {current_progress.get('notes', [])}

ANALYSIS:
- Priority Areas: {analysis.get('priority_areas', [])}
- Pending Items: {analysis.get('pending_items', [])}
- Technical Debt: {analysis.get('technical_debt', [])}

Create a JSON plan with the following structure:
{{
    "summary": "Brief description of the refinement plan",
    "description": "Detailed description of what will be accomplished",
    "priority": "high|medium|low",
    "estimated_effort": "small|medium|large",
    "goals": ["goal1", "goal2", "goal3"],
    "files_to_modify": ["file1.py", "file2.py"],
    "tests_to_add": ["test1", "test2"],
    "dependencies": ["dependency1", "dependency2"],
    "risks": ["risk1", "risk2"],
    "success_criteria": ["criteria1", "criteria2"]
}}

Focus on the next logical step in the development process. Be specific and actionable.
"""
        return prompt

    def _create_preparation_plan(self, analysis: Dict) -> Dict:
        """Create a plan for preparation phase."""
        return {
            "summary": "Complete preparation phase setup",
            "description": "Establish foundational components and testing framework",
            "priority": "high",
            "estimated_effort": "medium",
            "goals": [
                "Finalize spec documentation",
                "Set up basic project structure",
                "Create initial test framework",
                "Establish progress tracking"
            ],
            "files_to_modify": [
                "spec.md",
                "progress.md",
                "test_framework.py"
            ],
            "tests_to_add": [
                "basic_system_test",
                "spec_validation_test"
            ],
            "dependencies": [],
            "risks": [
                "Incomplete specification",
                "Missing test infrastructure"
            ],
            "success_criteria": [
                "All basic components implemented",
                "Initial tests passing",
                "Progress tracking functional"
            ]
        }

    def _create_refinement_plan(self, analysis: Dict) -> Dict:
        """Create a plan for refinement phase."""
        pending_items = analysis.get("pending_items", [])
        technical_debt = analysis.get("technical_debt", [])

        goals = ["Implement pending features", "Resolve technical issues"]
        if pending_items:
            goals.extend([f"Complete: {item[:50]}" for item in pending_items[:2]])

        return {
            "summary": "Advance refinement implementation",
            "description": "Implement pending features and resolve technical issues",
            "priority": "high",
            "estimated_effort": "medium",
            "goals": goals,
            "files_to_modify": [
                "reb00t/helix/agentic_system.py",
                "reb00t/helix/progress.py",
                "reb00t/helix/agent.py"
            ],
            "tests_to_add": [
                "integration_test",
                "refinement_cycle_test"
            ],
            "dependencies": [
                "progress_manager",
                "agent_framework"
            ],
            "risks": [
                "Integration complexity",
                "Test failures"
            ],
            "success_criteria": [
                "All pending items completed",
                "Integration tests passing",
                "No technical debt remaining"
            ]
        }

    def _create_default_plan(self, analysis: Dict) -> Dict:
        """Create a default plan when step is unclear."""
        return {
            "summary": "Analyze and plan next steps",
            "description": "Analyze current state and determine next development priorities",
            "priority": "medium",
            "estimated_effort": "small",
            "goals": [
                "Assess current project state",
                "Identify next priorities",
                "Update progress tracking"
            ],
            "files_to_modify": [
                "progress.md"
            ],
            "tests_to_add": [],
            "dependencies": [],
            "risks": [
                "Unclear project direction"
            ],
            "success_criteria": [
                "Clear next steps identified",
                "Progress updated"
            ]
        }

    def _validate_and_enhance_plan(self, plan: Dict) -> Dict:
        """Validate and enhance the generated plan."""
        # Ensure required fields exist
        required_fields = ["summary", "description", "goals", "files_to_modify", "tests_to_add"]
        for field in required_fields:
            if field not in plan:
                plan[field] = []

        # Add metadata
        plan["created_at"] = self._get_timestamp()
        plan["plan_id"] = f"plan_{len(self.plan_history) + 1}"

        # Validate goals are actionable
        if not plan["goals"]:
            plan["goals"] = ["Continue development according to spec"]

        # Ensure priority is set
        if "priority" not in plan:
            plan["priority"] = "medium"

        # Add default success criteria if missing
        if "success_criteria" not in plan or not plan["success_criteria"]:
            plan["success_criteria"] = [
                "All goals completed successfully",
                "Tests passing",
                "Progress updated"
            ]

        return plan

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_plan_history(self) -> List[Dict]:
        """Get the history of generated plans."""
        return self.plan_history.copy()


# --- Example usage: ---
if __name__ == "__main__":
    # Example usage
    planner = PlannerAgent()

    # Sample spec and progress
    sample_spec = """
    # Spec: Automated Development System
    ## Core Components
    1. **Living Specification** - Single source of truth
    2. **Progress Tracking** - Track development progress
    3. **Agent System** - Automated development agent
    """

    sample_progress = {
        "step": "B: Refinement, step 1",
        "details": ["Planning next refinement", "Awaiting user feedback"],
        "notes": ["Agent system partially implemented", "Need progress integration"]
    }

    # Generate plan
    result = planner.create_plan(sample_spec, sample_progress)

    if result["success"]:
        plan = result["plan"]
        print("Generated Plan:")
        print(f"Summary: {plan['summary']}")
        print(f"Goals: {plan['goals']}")
        print(f"Priority: {plan['priority']}")
        print(f"Files to modify: {plan['files_to_modify']}")
    else:
        print(f"Plan generation failed: {result['error']}")
