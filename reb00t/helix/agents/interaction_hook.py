# interaction_hook.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import sys


class InteractionHook(ABC):
    """Abstract base class for handling user interactions during agent execution."""

    @abstractmethod
    def request_user_feedback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request feedback from the user and block until response is received.

        Args:
            context: Dictionary containing context information for the user

        Returns:
            Dictionary containing user feedback with 'text' and 'continue' keys
        """
        pass


class CLIInteractionHook(InteractionHook):
    """Command-line interface implementation of InteractionHook."""

    def request_user_feedback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request feedback from the user via command line and block until response.

        Args:
            context: Dictionary containing context information for the user

        Returns:
            Dictionary containing user feedback with 'text' and 'continue' keys
        """
        print("\n" + "="*60)
        print("USER FEEDBACK REQUIRED")
        print("="*60)

        # Display context information
        if "title" in context:
            print(f"Context: {context['title']}")

        if "plan" in context:
            plan = context["plan"]
            print(f"\nProposed Plan: {plan.get('summary', 'No summary')}")
            print(f"Description: {plan.get('description', 'No description')}")
            print(f"Priority: {plan.get('priority', 'Unknown')}")
            print(f"Goals: {plan.get('goals', [])}")
            print(f"Files to modify: {plan.get('files_to_modify', [])}")

        if "message" in context:
            print(f"\n{context['message']}")

        print("\n" + "-"*60)
        print("Please provide your feedback:")
        print("(Leave empty to approve as-is, or type 'quit' to stop)")

        # Get user input
        try:
            feedback_text = input("Your feedback: ").strip()

            if feedback_text.lower() in ['quit', 'exit', 'stop']:
                should_continue = False
                feedback_text = "User requested to stop"
            else:
                # Ask if they want to continue
                continue_prompt = "Continue with refinement? (y/n, default: y): "
                continue_response = input(continue_prompt).strip().lower()
                should_continue = continue_response in ['', 'y', 'yes', 'true', '1']

            print("="*60)

            return {
                "text": feedback_text,
                "continue": should_continue
            }

        except (KeyboardInterrupt, EOFError):
            print("\nUser interrupted. Stopping refinement.")
            return {
                "text": "User interrupted",
                "continue": False
            }


class MockInteractionHook(InteractionHook):
    """Mock implementation for testing that auto-approves all requests."""

    def __init__(self, auto_continue: bool = True, default_feedback: str = ""):
        self.auto_continue = auto_continue
        self.default_feedback = default_feedback
        self.interaction_count = 0

    def request_user_feedback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock feedback that automatically responds without user interaction.

        Args:
            context: Dictionary containing context information

        Returns:
            Dictionary containing mock feedback with 'text' and 'continue' keys
        """
        self.interaction_count += 1

        return {
            "text": self.default_feedback,
            "continue": self.auto_continue
        }


class WebhookInteractionHook(InteractionHook):
    """Implementation that can be extended for web-based or API-based interactions."""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.pending_feedback = None

    def request_user_feedback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request feedback via webhook (placeholder implementation).
        In a real implementation, this would send the context to a web service
        and wait for the response.
        """
        # This is a placeholder - in a real implementation you would:
        # 1. Send context to webhook_url
        # 2. Wait for response (polling or websocket)
        # 3. Return the response

        raise NotImplementedError("WebhookInteractionHook requires implementation of actual webhook handling")
