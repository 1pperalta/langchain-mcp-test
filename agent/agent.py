"""Main LangChain agent for portfolio analysis."""
from typing import Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from agent.llm_client import create_llm
from agent.tools import create_portfolio_tools
from agent.usage_tracker import UsageTracker
from config import config


AGENT_PROMPT = """You are a helpful financial assistant for a Colombian investment portfolio.

You have access to tools to analyze the user's portfolio across multiple platforms (Lulo, Trii, Dolar App, etc.).

When answering questions:
1. Be concise and clear
2. Use specific numbers and percentages
3. Provide actionable insights when relevant
4. Always use tools to get real data - don't make assumptions
5. Format currency values clearly (COP vs USD)

Answer the following questions as best you can. You have access to the following tools:

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
Thought:{agent_scratchpad}"""


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
            print(f"\n⚠️  Budget Alert: {status['status']}")
            print(f"   Spent: ${status['total_spent']:.4f} / ${status['total_limit']:.2f}")
            print(f"   Remaining: ${status['total_remaining']:.4f}\n")
    
    def _initialize_agent(self, query_type: str = "general") -> None:
        """Initialize or reinitialize the agent with tracker."""
        self.llm = create_llm(
            temperature=0.3,
            tracker=self.tracker,
            query_type=query_type
        )
        
        prompt = PromptTemplate.from_template(AGENT_PROMPT)
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
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