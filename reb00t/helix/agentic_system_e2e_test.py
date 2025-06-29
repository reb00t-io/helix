from reb00t.helix.agentic_system import AgenticSystem
import os

def test_agentic_system_e2e():
    test_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test_data")
    os.chdir(test_data_dir)

    # Change to test_data directory so load_spec() finds the test spec.md
    sys = AgenticSystem()
    # 1. Load spec from current directory (test_data/spec.md) and playbook
    sys.load_spec()  # Will find spec.md in current directory

    # Verify that the actual spec content was loaded
    assert sys.spec is not None, "Spec should be loaded"
    assert "E2ETestDummy - Automated Spec-to-Production Software Development System" in sys.spec, "Should contain spec title"
    assert "Living Specification" in sys.spec, "Should contain core component info"
    assert "Playbook & Progress Beacon" in sys.spec, "Should contain playbook info"
    assert "LLM Agent (Bot)" in sys.spec, "Should contain agent info"

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
    assert sys.current_step() == "E2E"        # 4. Agent acts at E2E step
    agent_out = sys.run_agent({})
    assert "# TODO for step E2E" in agent_out

    # 5. Advance to DONE step
    assert sys.advance_step()
    assert sys.current_step() == "DONE"

    # 6. Test progress functionality
    initial_progress = sys.load_progress()
    assert initial_progress is not None
    assert "step" in initial_progress

    # Add a progress note
    sys.add_progress_note("E2E test completed successfully")
    updated_progress = sys.load_progress()
    assert "E2E test completed successfully" in updated_progress["notes"]

    # 7. All history is logged and contains actual spec content
    hist = sys.get_history()
    assert any(e["event"] == "spec_loaded" for e in hist)
    assert any(e["event"] == "step_advanced" for e in hist)
    assert any(e["event"] == "progress_loaded" for e in hist)
    assert any(e["event"] == "progress_note_added" for e in hist)
    assert len(hist) >= 7  # spec, playbook, progress, two advances, one agent run, note added

    # Verify that the spec_loaded event contains the actual spec content
    spec_loaded_event = next(e for e in hist if e["event"] == "spec_loaded")
    assert "Automated Spec-to-Production Software Development System" in spec_loaded_event["data"]["spec"]
    assert "spec.md" in spec_loaded_event["data"]["source"]

    print("✅ e2e test for agentic system: PASS")


# If running as script, call the test
if __name__ == "__main__":
    test_agentic_system_e2e()
