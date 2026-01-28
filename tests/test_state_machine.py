import unittest
from unittest.mock import MagicMock, patch
import sys
import json

# MOCK DEPENDENCIES BEFORE IMPORTING APP MODULES
# This allows running tests even if openai/numpy are not installed in the environment
mock_openai = MagicMock()
sys.modules["openai"] = mock_openai
mock_numpy = MagicMock()
sys.modules["numpy"] = mock_numpy

# Now we can import the modules that use these dependencies
try:
    from src.agent import ComplianceAgent
    from src.states.idle import IdleState
    from src.states.analysis import AnalysisState
    from src.states.audit import AuditState
    from src.states.final_response import FinalResponseState
except ImportError:
    # If imports fail due to other reasons, we want to know
    raise

class TestAgentStateMachine(unittest.TestCase):
    
    def setUp(self):
        self.mock_client = MagicMock()
        # Ensure the mock client is passed correctly
        self.agent = ComplianceAgent(client=self.mock_client, initial_state=IdleState())

    def test_idle_to_analysis(self):
        """Test transition from Idle to Analysis."""
        self.agent.current_query = "Test Query"
        self.assertIsInstance(self.agent._state, IdleState)
        
        self.agent.run() # Idle handles logic and transitions
        
        self.assertIsInstance(self.agent._state, AnalysisState)
        self.assertEqual(self.agent.history[0]["content"], "Test Query")

    def test_analysis_to_audit(self):
        """Test transition from Analysis to Audit when tool is called."""
        # Set agent to AnalysisState
        self.agent._state = AnalysisState()
        self.agent.history = [{"role": "user", "content": "Test"}]
        
        # Mock OpenAI response with tool call
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = None
        mock_message.tool_calls = [
            MagicMock(id="call_123", function=MagicMock(arguments='{"prompt_context": "ctx", "proposed_decision": "APROVADO"}'))
        ]
        mock_response.choices = [MagicMock(message=mock_message)]
        self.mock_client.chat.completions.create.return_value = mock_response
        
        self.agent.run()
        
        self.assertIsInstance(self.agent._state, AuditState)
        self.assertIsNotNone(self.agent.current_tool_call)

    def test_audit_to_final_response(self):
        """Test transition from Audit to FinalResponse."""
        self.agent._state = AuditState()
        
        # Setup mock tool call context
        mock_tool_call = MagicMock(id="call_123")
        mock_tool_call.function.arguments = json.dumps({"prompt_context": "ctx", "proposed_decision": "APROVADO"})
        self.agent.current_tool_call = mock_tool_call
        
        # Mock tool execution
        # We need to mock the tool object inside agent or its methods
        self.agent.tool.audit = MagicMock(return_value='{"decision": "APROVADO"}')
        
        self.agent.run()
        
        self.assertIsInstance(self.agent._state, FinalResponseState)
        # Check if tool output was added to history
        self.assertEqual(self.agent.history[-1]["role"], "tool")

    def test_final_response_to_idle(self):
        """Test transition from FinalResponse back to Idle."""
        self.agent._state = FinalResponseState()
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = "Final Answer"
        mock_response.choices = [MagicMock(message=mock_message)]
        self.mock_client.chat.completions.create.return_value = mock_response
        
        self.agent.run()
        
        self.assertIsInstance(self.agent._state, IdleState)

if __name__ == '__main__':
    unittest.main()
