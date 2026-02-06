"""Main LangChain agent for portfolio analysis."""
from typing import Optional
from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from agent.llm_client import create_llm
from agent.tools import create_portfolio_tools
from agent.usage_tracker import UsageTracker
from config import config


REACT_PROMPT = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")


class PortfolioAgent:
    """Main agent for portfolio analysis."""
    
    def __init__(self, tracker: Optional[UsageTracker] = None):
        if tracker is None:
            tracker = UsageTracker(
                budget_limit=config.BUDGET_LIMIT,
                daily_limit=config.DAILY_LIMIT
            )
        
        self.tracker = tracker
        self.tools = create_portfolio_tools()
        self.llm = None
        self.agent_executor = None
    
    def _check_budget(self) -> None:
        """Check if request is within budget before proceeding."""
        can_proceed, message = self.tracker.can_make_request()
        if not can_proceed:
            raise ValueError(f"Budget limit exceeded: {message}")
        
        status = self.tracker.get_budget_status()
        if status['status'] in ['WARNING', 'CRITICAL']:
            print(f"\nBudget Alert: {status['status']}")
            print(f"   Spent: ${status['total_spent']:.4f} / ${status['total_limit']:.2f}")
            print(f"   Remaining: ${status['total_remaining']:.4f}\n")
    
    def _initialize_agent(self, query_type: str = "general") -> None:
        """Initialize or reinitialize the agent with tracker."""
        self.llm = create_llm(
            temperature=0.3,
            tracker=self.tracker,
            query_type=query_type
        )
        
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def query(self, question: str, query_type: str = "general") -> str:
        """
        Process a user question about their portfolio.
        
        Args:
            question: User's question
            query_type: Type of query for tracking (e.g., "summary", "allocation", "analysis")
        
        Returns:
            Agent's response
        """
        self._check_budget()
        self._initialize_agent(query_type)
        
        try:
            result = self.agent_executor.invoke({"input": question})
            return result['output']
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def get_budget_status(self) -> dict:
        """Get current budget status."""
        return self.tracker.get_budget_status()