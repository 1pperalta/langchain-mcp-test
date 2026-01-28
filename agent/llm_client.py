"""LLM client configuration for OpenRouter."""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from config import config
from agent.usage_tracker import UsageTracker


class TokenCounterCallback(BaseCallbackHandler):
    """Callback to track token usage and costs."""
    
    def __init__(self, tracker: UsageTracker, query_type: str = "general"):
        self.tracker = tracker
        self.query_type = query_type
        self.input_tokens = 0
        self.output_tokens = 0
    
    def on_llm_start(self, serialized: dict, prompts: list[str], **kwargs) -> None:
        """Estimate input tokens when LLM starts."""
        for prompt in prompts:
            self.input_tokens += len(prompt.split()) * 1.3
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Track actual token usage when LLM completes."""
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            self.input_tokens = token_usage.get('prompt_tokens', self.input_tokens)
            self.output_tokens = token_usage.get('completion_tokens', 0)
            
            cost = self._calculate_cost(
                config.LLM_MODEL,
                self.input_tokens,
                self.output_tokens
            )
            
            self.tracker.record_usage(
                model=config.LLM_MODEL,
                input_tokens=int(self.input_tokens),
                output_tokens=self.output_tokens,
                cost=cost,
                query_type=self.query_type
            )
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model and token usage."""
        costs = {
            'openai/gpt-3.5-turbo': {
                'input': 0.0015 / 1000,
                'output': 0.002 / 1000
            },
            'anthropic/claude-3-haiku': {
                'input': 0.00025 / 1000,
                'output': 0.00125 / 1000
            },
            'google/gemini-flash-1.5': {
                'input': 0.00035 / 1000,
                'output': 0.00105 / 1000
            },
        }
        
        model_costs = costs.get(model, costs['openai/gpt-3.5-turbo'])
        return (input_tokens * model_costs['input']) + (output_tokens * model_costs['output'])


def create_llm(
    temperature: float = 0.3,
    tracker: Optional[UsageTracker] = None,
    query_type: str = "general"
) -> ChatOpenAI:
    """
    Create LangChain LLM instance configured for OpenRouter.
    
    Args:
        temperature: Creativity level (0.0 = deterministic, 1.0 = creative)
        tracker: Usage tracker instance
        query_type: Type of query for tracking
    
    Returns:
        Configured ChatOpenAI instance
    """
    if not config.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured in .env file")
    
    callbacks = []
    if tracker:
        callbacks.append(TokenCounterCallback(tracker, query_type))
    
    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        temperature=temperature,
        openai_api_key=config.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        callbacks=callbacks,
        default_headers={
            "HTTP-Referer": "https://github.com/your-repo",
            "X-Title": "Colombian Portfolio Aggregator"
        }
    )
    
    return llm