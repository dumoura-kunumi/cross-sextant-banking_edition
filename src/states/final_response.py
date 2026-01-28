"""
Final Response State - Generates the final response to the user.

This state calls the LLM with the complete conversation history (including
the audit result) to generate a final, user-friendly response.
"""

from typing import Any
from src.states.base import AgentState


class FinalResponseState(AgentState):
    """
    Generates the final response to the user based on the tool output and history.
    
    This state:
    1. Calls the LLM with the complete conversation history (including audit result)
    2. Generates a user-friendly final response
    3. Adds the response to history
    4. Transitions back to IdleState for the next query
    """
    
    FINAL_RESPONSE_SYSTEM_PROMPT = """You are a Compliance Agent providing final responses to users.

You have access to audit results from the ISR (Information Sufficiency Ratio) semantic analysis tool.
Your role is to:
1. Interpret the audit results clearly
2. Provide a user-friendly explanation of the decision
3. Include relevant metrics (ISR, confidence, etc.) when appropriate
4. Be transparent about the auditing process

The audit result will be in the conversation history as a tool response.
Use it to inform your final answer to the user."""

    def handle(self, context: Any) -> None:
        """
        Handles the final response state logic.
        
        Args:
            context: The ComplianceAgent context instance
        """
        print(f"[{self.__class__.__name__}] Generating final response to user...")
        
        try:
            # Prepare messages with system prompt
            # The history already contains: user query, assistant tool call, tool result
            messages = [{"role": "system", "content": self.FINAL_RESPONSE_SYSTEM_PROMPT}] + context.history
            
            # Call LLM to generate final response
            response = context.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7  # Slightly higher temperature for more natural responses
            )
            
            message = response.choices[0].message
            
            # Add final response to history
            context.add_message(
                role=message.role,
                content=message.content
            )
            
            # Display the final response
            print("\n" + "="*70)
            print(">>> AGENT FINAL RESPONSE:")
            print("="*70)
            print(message.content)
            print("="*70 + "\n")
            
            # Transition back to IdleState for the next query
            # This completes the state machine cycle:
            # Idle -> Analysis -> Audit -> FinalResponse -> Idle
            from src.states.idle import IdleState
            context.transition_to(IdleState())
            
        except Exception as e:
            print(f"[{self.__class__.__name__}] ERROR: Failed to generate final response: {e}")
            import traceback
            traceback.print_exc()
            
            # Even on error, transition back to Idle to allow next query
            from src.states.idle import IdleState
            context.transition_to(IdleState())
