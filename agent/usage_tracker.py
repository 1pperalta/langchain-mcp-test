"""Usage tracking and budget management using JSON."""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class UsageRecord:
    """Record of a single API call."""
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    query_type: str


class UsageTracker:
    """Track API usage and enforce budget limits using JSON."""
    
    def __init__(
        self,
        json_path: Optional[Path] = None,
        budget_limit: float = 5.0,
        daily_limit: float = 0.25
    ):
        if json_path is None:
            json_path = Path(__file__).parent.parent / 'usage.json'
        
        self.json_path = json_path
        self.budget_limit = budget_limit
        self.daily_limit = daily_limit
        self._init_file()
    
    def _init_file(self) -> None:
        """Initialize JSON file if it doesn't exist."""
        if not self.json_path.exists():
            self._save_data([])
    
    def _load_data(self) -> list[dict]:
        """Load usage data from JSON."""
        if not self.json_path.exists():
            return []
        
        with open(self.json_path, 'r') as f:
            return json.load(f)
    
    def _save_data(self, data: list[dict]) -> None:
        """Save usage data to JSON."""
        with open(self.json_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        query_type: str = "general"
    ) -> None:
        """Record an API call."""
        data = self._load_data()
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'query_type': query_type
        }
        
        data.append(record)
        self._save_data(data)
    
    def get_total_spent(self) -> float:
        """Get total amount spent."""
        data = self._load_data()
        return sum(record['cost'] for record in data)
    
    def get_daily_spent(self) -> float:
        """Get amount spent today."""
        data = self._load_data()
        today = datetime.now().date()
        
        daily_total = 0.0
        for record in data:
            record_date = datetime.fromisoformat(record['timestamp']).date()
            if record_date == today:
                daily_total += record['cost']
        
        return daily_total
    
    def can_make_request(self, estimated_cost: float = 0.01) -> tuple[bool, str]:
        """Check if request is within budget limits."""
        total_spent = self.get_total_spent()
        daily_spent = self.get_daily_spent()
        
        if total_spent + estimated_cost > self.budget_limit:
            remaining = self.budget_limit - total_spent
            return False, f"Budget limit reached. Total: ${total_spent:.4f} / ${self.budget_limit:.2f}. Remaining: ${remaining:.4f}"
        
        if daily_spent + estimated_cost > self.daily_limit:
            remaining = self.daily_limit - daily_spent
            return False, f"Daily limit reached. Today: ${daily_spent:.4f} / ${self.daily_limit:.2f}. Remaining: ${remaining:.4f}"
        
        return True, "OK"
    
    def get_budget_status(self) -> dict:
        """Get current budget status."""
        total_spent = self.get_total_spent()
        daily_spent = self.get_daily_spent()
        
        total_remaining = self.budget_limit - total_spent
        daily_remaining = self.daily_limit - daily_spent
        total_percent = (total_spent / self.budget_limit) * 100 if self.budget_limit > 0 else 0
        
        return {
            'total_spent': total_spent,
            'total_limit': self.budget_limit,
            'total_remaining': total_remaining,
            'total_percent': total_percent,
            'daily_spent': daily_spent,
            'daily_limit': self.daily_limit,
            'daily_remaining': daily_remaining,
            'status': self._get_status_level(total_percent)
        }
    
    def _get_status_level(self, percent: float) -> str:
        """Get status level based on usage percentage."""
        if percent >= 95:
            return 'CRITICAL'
        elif percent >= 80:
            return 'WARNING'
        elif percent >= 50:
            return 'CAUTION'
        else:
            return 'OK'
    
    def get_usage_history(self, days: int = 7) -> list[UsageRecord]:
        """Get usage history for the last N days."""
        data = self._load_data()
        cutoff = datetime.now() - timedelta(days=days)
        
        history = []
        for record in data:
            record_time = datetime.fromisoformat(record['timestamp'])
            if record_time >= cutoff:
                history.append(UsageRecord(
                    timestamp=record['timestamp'],
                    model=record['model'],
                    input_tokens=record['input_tokens'],
                    output_tokens=record['output_tokens'],
                    cost=record['cost'],
                    query_type=record['query_type']
                ))
        
        return sorted(history, key=lambda x: x.timestamp, reverse=True)