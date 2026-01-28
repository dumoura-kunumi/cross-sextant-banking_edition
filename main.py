"""
Main entry point for the Compliance Agent with State Design Pattern.

This script initializes the agent and runs the interactive loop.
The agent uses a State Machine to process queries through:
IdleState -> AnalysisState -> AuditState -> FinalResponseState -> IdleState
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from src.agent import ComplianceAgent
from src.states.idle import IdleState


def main():
    """
    Main function that initializes and runs the Compliance Agent.
    
    The agent processes user queries through a state machine:
    1. IdleState: Captures user input
    2. AnalysisState: Analyzes intent and calls audit tool
    3. AuditState: Executes ISR semantic audit
    4. FinalResponseState: Generates final response
    5. Returns to IdleState for next query
    """
    # Setup OpenAI Client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with: OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}")
        sys.exit(1)
    
    # Initialize Agent with IdleState
    agent = ComplianceAgent(client=client, initial_state=IdleState())
    
    print("\n" + "="*70)
    print(">>> Semantic ISR Auditor Agent Initialized <<<")
    print("="*70)
    print("\nThis agent uses ISR (Information Sufficiency Ratio) to audit decisions.")
    print("State Machine Flow: Idle -> Analysis -> Audit -> FinalResponse -> Idle")
    print("\nType 'exit' or 'quit' to stop the agent.\n")
    
    try:
        while True:
            # Get user input
            user_input = input("Enter your query: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nExiting agent...")
                break
            
            # Set the query in the agent context
            agent.current_query = user_input
            
            # Run the state machine until we return to IdleState
            # The state machine will process:
            # 1. IdleState: Adds query to history, transitions to AnalysisState
            # 2. AnalysisState: Calls LLM, extracts tool call, transitions to AuditState
            # 3. AuditState: Executes ISR audit, transitions to FinalResponseState
            # 4. FinalResponseState: Generates final response, transitions to IdleState
            
            max_iterations = 20  # Safety limit to prevent infinite loops
            iteration = 0
            
            while not isinstance(agent._state, IdleState) and iteration < max_iterations:
                agent.run()
                iteration += 1
            
            if iteration >= max_iterations:
                print(f"\nWARNING: State machine exceeded {max_iterations} iterations.")
                print("Resetting to IdleState...")
                agent.transition_to(IdleState())
            
            print("\n" + "-"*70 + "\n")
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nAgent shutdown complete.")


if __name__ == "__main__":
    main()
