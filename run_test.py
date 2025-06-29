#!/usr/bin/env python3
"""Simple test runner for the agentic system."""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the test
from reb00t.helix.agentic_system_e2e_test import test_agentic_system_e2e

if __name__ == "__main__":
    try:
        test_agentic_system_e2e()
        print("✅ All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
