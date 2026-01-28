"""
Analysis State - Analyzes user intent and determines if audit is needed.

This state sends the user query to the LLM with a strict system prompt
that requires the use of the audit tool before making any decisions.
"""

import json
from typing import Any
from src.states.base import AgentState


class AnalysisState(AgentState):
    """
    Analyzes the user intent using LLM.
    
    This state:
    1. Sends the user query to the LLM with a strict compliance system prompt
    2. Forces the LLM to use the audit tool for any decision-making
    3. Extracts tool call arguments if the tool is called
    4. Transitions to AuditState if tool is called, or FinalResponseState if not
    """
    
    SYSTEM_PROMPT = """You are a Compliance Agent specialized in fact verification and decision auditing.

CRITICAL RULES:
1. You MUST NOT make final decisions (APPROVE/REJECT/APROVADO/BLOQUEADO) without using the 'audit' tool first.
2. For ANY request that requires a decision or fact verification, you MUST call the 'audit' tool.
3. The 'audit' tool performs semantic ISR (Information Sufficiency Ratio) analysis to detect hallucinations.
4. Only AFTER the audit tool returns its result, you can provide the final answer to the user.
5. If the user asks a simple question that doesn't require auditing, you may respond directly.

When calling the audit tool:
- prompt_context: The original user query/question and any relevant context
- proposed_decision: Your proposed decision token (e.g., "APROVADO", "BLOQUEADO", "APPROVE", "REJECT")

Remember: Compliance and accuracy are paramount. Always audit before deciding."""

    def handle(self, context: Any) -> None:
        """
        Handles the analysis state logic.
        
        Args:
            context: The ComplianceAgent context instance
        """
        print(f"[{self.__class__.__name__}] Analyzing user intent with LLM...")
        
        # Prepare tools definition for the LLM
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "audit",
                    "description": (
                        "Audits a proposed decision using ISR (Information Sufficiency Ratio) "
                        "Semantic Analysis. This tool detects hallucinations and verifies if a "
                        "decision is supported by the context. ALWAYS use this tool before making "
                        "any final decision."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt_context": {
                                "type": "string",
                                "description": (
                                    "The original user prompt/question and any relevant context. "
                                    "This is the full context that will be audited."
                                )
                            },
                            "proposed_decision": {
                                "type": "string",
                                "description": (
                                    "The proposed decision token you want to verify. "
                                    "Examples: 'APROVADO', 'BLOQUEADO', 'APPROVE', 'REJECT', 'YES', 'NO'. "
                                    "This represents your initial assessment before auditing."
                                ),
                                "enum": ["APROVADO", "BLOQUEADO", "APPROVE", "REJECT", "YES", "NO"]
                            }
                        },
                        "required": ["prompt_context", "proposed_decision"]
                    }
                }
            }
        ]

        # Prepare messages: system prompt + conversation history
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}] + context.history
        
        try:
            # Call LLM with tools enabled
            response = context.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"  # Let LLM decide, but system prompt strongly encourages tool use
            )
            
            message = response.choices[0].message
            
            # Add assistant message to history
            context.add_message(
                role=message.role,
                content=message.content,
                tool_calls=message.tool_calls if hasattr(message, 'tool_calls') and message.tool_calls else None
            )
            
            # Check if LLM called the audit tool
            if message.tool_calls and len(message.tool_calls) > 0:
                # Extract the first tool call (we expect only one audit call)
                tool_call = message.tool_calls[0]
                
                # Validate it's the audit tool
                if tool_call.function.name == "audit":
                    context.current_tool_call = tool_call
                    print(f"[{self.__class__.__name__}] LLM requested audit tool. Extracting arguments...")
                    
                    # Transition to AuditState
                    from src.states.audit import AuditState
                    context.transition_to(AuditState())
                else:
                    # Unexpected tool call
                    print(f"[{self.__class__.__name__}] Warning: Unexpected tool call: {tool_call.function.name}")
                    from src.states.final_response import FinalResponseState
                    context.transition_to(FinalResponseState())
            else:
                # LLM didn't call the tool
                # This could mean:
                # 1. The query doesn't require auditing (simple question)
                # 2. The LLM failed to follow instructions
                print(f"[{self.__class__.__name__}] LLM did not call the audit tool. Proceeding to final response.")
                from src.states.final_response import FinalResponseState
                context.transition_to(FinalResponseState())
                
        except Exception as e:
            print(f"[{self.__class__.__name__}] Error during analysis: {e}")
            # Transition to ErrorState or FinalResponseState
            from src.states.final_response import FinalResponseState
            context.transition_to(FinalResponseState())
