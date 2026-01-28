"""
Audit State - Executes the ISR Semantic Audit.

This state runs the complete ISR v3 audit logic including:
- Delta calculation (information gain)
- B2T calculation (Bits-to-Trust, KL Divergence)
- JS Bound calculation (instability measure)
- ISR calculation (Information Sufficiency Ratio)
- All 4 critical patches (Laplace, Clipping, Hard Veto, Success Shortcut)
"""

import json
from typing import Any
from src.states.base import AgentState


class AuditState(AgentState):
    """
    Executes the SemanticISRAuditorTool logic.
    
    This state:
    1. Extracts tool call arguments (prompt_context, proposed_decision)
    2. Executes the ISR audit tool with complete mathematical logic
    3. Adds the audit result to the conversation history
    4. Stores the result for potential use in FinalResponseState
    5. Transitions to FinalResponseState
    """
    
    def handle(self, context: Any) -> None:
        """
        Handles the audit state logic.
        
        Args:
            context: The ComplianceAgent context instance
        """
        tool_call = getattr(context, 'current_tool_call', None)
        
        if not tool_call:
            print(f"[{self.__class__.__name__}] ERROR: No tool call found. Cannot execute audit.")
            from src.states.final_response import FinalResponseState
            context.transition_to(FinalResponseState())
            return

        print(f"[{self.__class__.__name__}] Executing ISR Semantic Audit...")
        
        try:
            # Parse tool call arguments
            args = json.loads(tool_call.function.arguments)
            prompt_context = args.get("prompt_context", "")
            proposed_decision = args.get("proposed_decision", "")
            
            if not prompt_context or not proposed_decision:
                raise ValueError("Missing required arguments: prompt_context or proposed_decision")
            
            print(f"[{self.__class__.__name__}] Auditing decision: '{proposed_decision}'")
            print(f"[{self.__class__.__name__}] Context: {prompt_context[:100]}...")
            
            # Execute the ISR audit tool
            # This runs the complete ISR v3 logic:
            # - Generates permutations
            # - Calculates probabilities
            # - Computes Delta, B2T, JS Bound, ISR
            # - Applies all 4 patches
            # - Returns decision (APROVADO/BLOQUEADO) with metrics
            result_json = context.tool.audit(prompt_context, proposed_decision)
            
            # Parse result for storage and logging
            try:
                audit_result = json.loads(result_json)
                context.audit_result = audit_result
                
                decision = audit_result.get("decision", "UNKNOWN")
                metrics = audit_result.get("metrics", {})
                isr = metrics.get("ISR", 0.0)
                reason = audit_result.get("reason", "")
                
                print(f"[{self.__class__.__name__}] Audit Complete!")
                print(f"[{self.__class__.__name__}] Decision: {decision}")
                print(f"[{self.__class__.__name__}] ISR: {isr}")
                print(f"[{self.__class__.__name__}] Reason: {reason}")
            except json.JSONDecodeError:
                # If result is not valid JSON, store as string
                context.audit_result = {"raw_result": result_json}
                print(f"[{self.__class__.__name__}] Audit result (raw): {result_json[:200]}...")
            
            # Add tool result to conversation history
            # This is critical - the LLM in FinalResponseState needs this to generate the final answer
            context.add_message(
                role="tool",
                content=result_json,
                tool_call_id=tool_call.id,
                name="audit"
            )
            
            # Transition to FinalResponseState
            # The LLM will now have access to the audit result and can generate the final response
            from src.states.final_response import FinalResponseState
            context.transition_to(FinalResponseState())
            
        except json.JSONDecodeError as e:
            print(f"[{self.__class__.__name__}] ERROR: Failed to parse tool call arguments: {e}")
            error_result = json.dumps({
                "decision": "BLOQUEADO",
                "metrics": {},
                "reason": f"Error parsing tool arguments: {str(e)}"
            })
            context.add_message(
                role="tool",
                content=error_result,
                tool_call_id=tool_call.id if tool_call else None,
                name="audit"
            )
            from src.states.final_response import FinalResponseState
            context.transition_to(FinalResponseState())
            
        except ValueError as e:
            print(f"[{self.__class__.__name__}] ERROR: Invalid arguments: {e}")
            error_result = json.dumps({
                "decision": "BLOQUEADO",
                "metrics": {},
                "reason": f"Invalid arguments: {str(e)}"
            })
            context.add_message(
                role="tool",
                content=error_result,
                tool_call_id=tool_call.id if tool_call else None,
                name="audit"
            )
            from src.states.final_response import FinalResponseState
            context.transition_to(FinalResponseState())
            
        except Exception as e:
            print(f"[{self.__class__.__name__}] ERROR: Unexpected error during audit execution: {e}")
            import traceback
            traceback.print_exc()
            
            error_result = json.dumps({
                "decision": "BLOQUEADO",
                "metrics": {},
                "reason": f"Unexpected error: {str(e)}"
            })
            context.add_message(
                role="tool",
                content=error_result,
                tool_call_id=tool_call.id if tool_call else None,
                name="audit"
            )
            from src.states.final_response import FinalResponseState
            context.transition_to(FinalResponseState())
