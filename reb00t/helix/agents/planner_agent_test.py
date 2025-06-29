import unittest
from reb00t.common.llm.llm import release_llm_instances
from reb00t.helix.agents.planner_agent import PlannerAgent

class TestPlannerAgent(unittest.TestCase):

    def setUp(self):
        release_llm_instances()
        self.planner = PlannerAgent()

    def test_initialize_planner(self):
        self.assertIsNotNone(self.planner)

    def test_create_plan_with_sample_data(self):
        sample_spec = """
        # Spec: Automated Development System

        ## Purpose
        Automate software development process

        ## Core Components
        1. **Living Specification** - Single source of truth for requirements
        2. **Progress Tracking** - Track development progress through steps
        3. **Agent System** - Automated development agent for code generation
        4. **Testing Framework** - Automated testing and validation

        ## Workflow
        ### A: Preparation
        1. Generate spec.md with requirements
        2. Generate progress.md with current state
        3. Generate basic system mockup
        4. Generate e2e test for system

        ## Invariants
        - The spec is the only source of truth
        - All changes must be tested
        """

        sample_progress = {
            "step": "B: Refinement, step 1",
            "details": [
                "Planning next refinement",
                "Awaiting user feedback/adjustment",
                "Need to integrate progress tracking"
            ],
            "notes": [
                "Agent system partially implemented",
                "E2E tests working",
                "Need progress manager integration",
                "Some technical debt in imports"
            ]
        }

        result = self.planner.create_plan(sample_spec, sample_progress)
        self.assertTrue(result["success"])
        self.assertIn("plan", result)
        self.assertIn("analysis", result)

        plan = result["plan"]
        required_fields = ["summary", "description", "goals", "files_to_modify", "tests_to_add", "success_criteria"]
        for field in required_fields:
            self.assertIn(field, plan)

        self.assertIsInstance(plan["goals"], list)
        self.assertGreater(len(plan["goals"]), 0)
        self.assertIsInstance(plan["files_to_modify"], list)

        analysis = result["analysis"]
        self.assertIn("current_step", analysis)
        self.assertIn("spec_requirements", analysis)
        self.assertIn("priority_areas", analysis)
        self.assertEqual(analysis["current_step"], "B: Refinement, step 1")

    def test_preparation_phase_planning(self):
        sample_spec = "Dummy Spec"
        prep_progress = {
            "step": "A: Preparation, step 2",
            "details": ["Setting up basic structure"],
            "notes": ["Initial setup in progress"]
        }

        prep_result = self.planner.create_plan(sample_spec, prep_progress)
        prep_plan = prep_result["plan"]
        self.assertTrue("preparation" in prep_plan["summary"].lower() or "setup" in prep_plan["summary"].lower())

    def test_plan_history(self):
        sample_spec = "Dummy Spec"
        dummy_progress = {"step": "Test Step", "details": [], "notes": []}
        self.planner.create_plan(sample_spec, dummy_progress)
        self.planner.create_plan(sample_spec, dummy_progress)

        history = self.planner.get_plan_history()
        self.assertEqual(len(history), 2)
        self.assertTrue(all("plan_id" in plan for plan in history))

    def test_error_handling(self):
        error_result = self.planner.create_plan("", {})
        self.assertTrue(error_result["success"])

    def test_complex_spec(self):
        complex_spec = """
        # Spec: E2ETestDummy - Automated Spec-to-Production Software Development System

        ## Purpose
        Automate the end-to-end software development process—from initial product idea through production deployment.

        ## Core Components
        1. **Living Specification** - Single source of truth for requirements, interfaces, invariants
        2. **Playbook & Progress Beacon** - Machine-readable playbook defines each phase
        3. **Atomic, Always-Green Commits** - Each commit addresses a single playbook step
        4. **LLM Agent (Bot)** - Reads current spec, playbook step, and repo context
        5. **CI/CD Integration** - CI enforces exit conditions for each playbook step

        ## Workflow
        ### B: Refinement loop
        1. plan next refinement; ask user for feedback / adjustment
        2. adjust e2e test according to plan
        3. implement refinement including unit tests
        4. check e2e test is passing
        5. review spec and decide if a change is needed
        6. commit changes
        7. continue with 1 or stop if completed
        """

        complex_progress = {
            "step": "B: Refinement, step 3",
            "details": [
                "Implementing refinement including unit tests",
                "Progress manager integration in progress",
                "Agent system needs coordination layer"
            ],
            "notes": [
                "Successfully integrated ProgressManager into AgenticSystem",
                "E2E tests updated and passing",
                "Need to add coordination between agents",
                "Some import issues resolved",
                "Ready for next implementation phase"
            ]
        }

        result = self.planner.create_plan(complex_spec, complex_progress)
        plan = result["plan"]
        self.assertGreaterEqual(len(plan["goals"]), 3)
        self.assertGreaterEqual(len(plan["files_to_modify"]), 2)
        self.assertIn(plan["priority"], ["high", "medium", "low"])
        self.assertIn("estimated_effort", plan)


if __name__ == "__main__":
    unittest.main()
