from reb00t.helix.agentic_system import AgenticSystem

def test_agentic_system_e2e():
    sys = AgenticSystem()
    # 1. Load spec and playbook
    sys.load_spec("Spec: Demo agentic system v1.0")
    sys.load_playbook({"steps": [
        {"id": "DRAFT", "goal": "Draft the spec"},
        {"id": "E2E", "goal": "Write red-bar e2e test"},
        {"id": "DONE", "goal": "All steps green"}
    ]})

    # 2. Initial step should be DRAFT
    assert sys.current_step() == "DRAFT"
    assert sys.run_agent({}).startswith("# TODO for step DRAFT")

    # 3. Advance to E2E step
    assert sys.advance_step()
    assert sys.current_step() == "E2E"

    # 4. Agent acts at E2E step
    agent_out = sys.run_agent({})
    assert "# TODO for step E2E" in agent_out

    # 5. Advance to DONE step
    assert sys.advance_step()
    assert sys.current_step() == "DONE"

    # 6. All history is logged
    hist = sys.get_history()
    assert any(e["event"] == "spec_loaded" for e in hist)
    assert any(e["event"] == "step_advanced" for e in hist)
    assert len(hist) >= 5  # At least spec, playbook, two advances, one agent run

    print("✅ e2e test for agentic system: PASS")

# If running as script, call the test
if __name__ == "__main__":
    test_agentic_system_e2e()
