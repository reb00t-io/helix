# planner_agent_test.py
import tempfile
import shutil
import os
from reb00t.helix.agents.planner_agent import PlannerAgent

def test_planner_agent():
    """Test the PlannerAgent functionality."""

    # Test 1: Initialize planner
    planner = PlannerAgent()
    assert planner is not None
    print("✅ Test 1 passed: Planner initialized successfully")

    # Test 2: Create plan with sample data
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

    result = planner.create_plan(sample_spec, sample_progress)

    assert result["success"] == True
    assert "plan" in result
    assert "analysis" in result
    print("✅ Test 2 passed: Plan created successfully")

    # Test 3: Validate plan structure
    plan = result["plan"]
    required_fields = ["summary", "description", "goals", "files_to_modify", "tests_to_add", "success_criteria"]

    for field in required_fields:
        assert field in plan, f"Missing required field: {field}"

    assert isinstance(plan["goals"], list)
    assert len(plan["goals"]) > 0
    assert isinstance(plan["files_to_modify"], list)
    print("✅ Test 3 passed: Plan structure is valid")

    # Test 4: Test analysis functionality
    analysis = result["analysis"]
    assert "current_step" in analysis
    assert "spec_requirements" in analysis
    assert "priority_areas" in analysis
    assert analysis["current_step"] == "B: Refinement, step 1"
    print("✅ Test 4 passed: Analysis functionality works")

    # Test 5: Test preparation phase planning
    prep_progress = {
        "step": "A: Preparation, step 2",
        "details": ["Setting up basic structure"],
        "notes": ["Initial setup in progress"]
    }

    prep_result = planner.create_plan(sample_spec, prep_progress)
    prep_plan = prep_result["plan"]

    assert "preparation" in prep_plan["summary"].lower() or "setup" in prep_plan["summary"].lower()
    print("✅ Test 5 passed: Preparation phase planning works")

    # Test 6: Test plan history
    history = planner.get_plan_history()
    assert len(history) == 2  # Two plans created
    assert all("plan_id" in plan for plan in history)
    print("✅ Test 6 passed: Plan history tracking works")

    # Test 7: Test error handling
    error_result = planner.create_plan("", {})  # Empty inputs
    assert error_result["success"] == True  # Should still work with fallback
    print("✅ Test 7 passed: Error handling works")

    # Test 8: Test spec requirement extraction
    requirements = planner._extract_spec_requirements(sample_spec)
    assert len(requirements) > 0
    assert any("Living Specification" in req for req in requirements)
    print("✅ Test 8 passed: Spec requirement extraction works")

    print("\n🎉 All planner tests passed!")


def test_planner_with_complex_spec():
    """Test planner with more complex specification."""
    planner = PlannerAgent()

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

    result = planner.create_plan(complex_spec, complex_progress)
    plan = result["plan"]

    # Should generate more sophisticated plan for complex input
    assert len(plan["goals"]) >= 3
    assert len(plan["files_to_modify"]) >= 2
    assert plan["priority"] in ["high", "medium", "low"]
    assert "estimated_effort" in plan

    print("✅ Complex spec test passed: Sophisticated plan generated")


if __name__ == "__main__":
    test_planner_agent()
    test_planner_with_complex_spec()
    print("\n✅ All planner agent tests completed successfully!")
