import json
import os
from typing import Optional

from book_agent_core.models import ContextSection, ContextPack
from book_agent_core.budget import BudgetEngine


DEFAULT_CATEGORIES = [
    ("book_bible", ["00-index/book-structure.md", "00-index/book-review.md"], 4000, 0),
    ("style_voice", ["00-index/style-composition.md", "00-index/voice-profile.md"], 3000, 0),
    ("current_state", ["truth/current_state.md"], 3000, 0),
    ("hook_ledger", ["truth/hook_ledger.md"], 3000, 1),
    ("argument_state", ["truth/argument_state.md"], 4000, 1),
    ("chapter_summaries", ["truth/chapter_summaries.md"], 4000, 1),
    ("evidence_ledger", ["truth/evidence_ledger.md"], 3000, 2),
    ("concept_cards", [], 3000, 2),
    ("cases", [], 3000, 2),
    ("character_board", ["truth/character_board.md"], 2000, 2),
]


class Composer:
    def __init__(self, book_dir: str, total_budget: int = 32000,
                 config_path: Optional[str] = None):
        self.book_dir = book_dir
        self.truth_dir = os.path.join(book_dir, "truth")
        self.runtime_dir = os.path.join(self.truth_dir, "runtime")
        if not config_path:
            config_path = os.path.join(book_dir, "composer_budget.yaml")
        if os.path.isfile(config_path):
            self.budget = BudgetEngine(config_path=config_path)
        else:
            self.budget = BudgetEngine(total_budget=total_budget)

    def _read_file(self, path: str) -> str:
        if not os.path.isfile(path):
            return ""
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()

    def _read_concept_cards(self) -> str:
        for dname in ["02-概念卡", "02-concept-cards"]:
            dpath = os.path.join(self.book_dir, dname)
            if os.path.isdir(dpath):
                parts = []
                for fn in sorted(os.listdir(dpath))[:5]:
                    fp = os.path.join(dpath, fn)
                    if fn.endswith(".md") and os.path.isfile(fp):
                        parts.append(self._read_file(fp)[:1000])
                return "\n---\n".join(parts)
        return ""

    def _read_cases(self) -> str:
        for dname in ["03-案例库", "04-case-bank"]:
            dpath = os.path.join(self.book_dir, dname)
            if os.path.isdir(dpath):
                parts = []
                for fn in sorted(os.listdir(dpath))[:5]:
                    fp = os.path.join(dpath, fn)
                    if fn.endswith(".md") and os.path.isfile(fp):
                        parts.append(self._read_file(fp)[:1000])
                return "\n---\n".join(parts)
        return ""

    def _get_content(self, category: str, paths: list) -> str:
        if category == "concept_cards":
            return self._read_concept_cards()
        if category == "cases":
            return self._read_cases()
        parts = []
        for p in paths:
            full = os.path.join(self.book_dir, p)
            content = self._read_file(full)
            if content:
                parts.append(content)
        return "\n---\n".join(parts)

    def compose(self, chapter_num: int) -> ContextPack:
        sections = []
        remaining = self.budget.total_budget
        truncated_report = []

        sorted_cats = sorted(DEFAULT_CATEGORIES, key=lambda x: (x[3], x[0]))

        for cat_name, paths, budget, priority in sorted_cats:
            content = self._get_content(cat_name, paths)
            if not content.strip():
                continue

            tokens = self.budget.estimate_tokens(content)

            if tokens > budget:
                content, tokens = self.budget.truncate_to_budget(content, budget)
                truncated_report.append(f"{cat_name}: truncated to {budget} tokens (original {self.budget.estimate_tokens(self._get_content(cat_name, paths))})")

            if tokens > remaining:
                truncated_report.append(f"{cat_name}: skipped (budget exhausted)")
                continue

            source_paths = paths if paths else [cat_name]
            summary = content[:80].replace("\n", " ") + "..."

            section = ContextSection(
                category=cat_name,
                source=", ".join(source_paths),
                reason=f"Chapter {chapter_num} writing context",
                summary=summary,
                content=content,
                tokens=tokens,
            )
            sections.append(section)
            remaining -= tokens

        budget_report = "All categories fit within budget."
        if truncated_report:
            budget_report = "Budget adjustments:\n" + "\n".join(f"  - {r}" for r in truncated_report)

        return ContextPack(
            sections=sections,
            total_tokens=self.budget.total_budget - remaining,
            budget_report=budget_report,
        )

    def save_context_pack(self, pack: ContextPack, chapter_num: int) -> str:
        os.makedirs(self.runtime_dir, exist_ok=True)
        out_path = os.path.join(self.runtime_dir, f"ch{chapter_num:02d}_context_pack.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(pack.to_dict(), f, ensure_ascii=False, indent=2)
        return out_path
