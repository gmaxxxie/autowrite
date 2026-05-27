import os
from typing import Optional


class BudgetEngine:
    TOKEN_RATIO = 1.5

    def __init__(self, total_budget: int = 32000, config_path: Optional[str] = None):
        self.total_budget = total_budget
        self.categories = {}
        if config_path and os.path.isfile(config_path):
            self._load_config(config_path)

    def _load_config(self, config_path: str):
        import yaml
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.total_budget = cfg.get("total_budget", self.total_budget)
        for cat_name, cat_cfg in cfg.get("categories", {}).items():
            self.categories[cat_name] = {
                "budget": cat_cfg.get("budget", 0),
                "priority": cat_cfg.get("priority", 2),
            }

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return int(len(text) / self.TOKEN_RATIO)

    def truncate_to_budget(self, text: str, budget: int) -> tuple:
        tokens = self.estimate_tokens(text)
        if tokens <= budget:
            return text, tokens
        max_chars = int(budget * self.TOKEN_RATIO)
        truncated = text[:max_chars] + f"\n...[truncated, 原文 {tokens} tokens]"
        return truncated, budget

    def allocate(self, categories: list) -> dict:
        sorted_cats = sorted(categories, key=lambda x: (x[2], x[0]))
        remaining = self.total_budget
        allocation = {}
        for name, budget, priority in sorted_cats:
            if remaining <= 0:
                break
            allocated = min(budget, remaining)
            allocation[name] = allocated
            remaining -= allocated
        return allocation
