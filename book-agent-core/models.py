from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Hook:
    hook_id: str
    type: str
    description: str
    seeded_in: str
    payoff_timing: str
    status: str = "seed"
    progress_chapters: list = field(default_factory=list)
    health: str = "on-track"


@dataclass
class Character:
    char_id: str
    name: str
    type: str
    personality_base: str
    speech_patterns: list = field(default_factory=list)
    info_boundary: str = ""
    pov_filter: str = ""
    chapters_appeared: list = field(default_factory=list)


@dataclass
class Argument:
    arg_id: str
    statement: str
    chapter_introduced: str
    status: str = "pending"
    supporting_evidence: list = field(default_factory=list)


@dataclass
class Evidence:
    ev_id: str
    ev_type: str
    description: str
    source: str = ""
    reliability: str = "unverified"
    chapter_used: str = ""


@dataclass
class ChapterSummary:
    chapter: str
    title: str
    word_count: int
    core_argument: str
    key_cases: list = field(default_factory=list)
    foreshadowing: list = field(default_factory=list)


@dataclass
class HookDelta:
    hook_id: str
    old_status: str
    new_status: str
    reason: str


@dataclass
class CharDelta:
    char_id: str
    field: str
    old_value: str
    new_value: str


@dataclass
class StateDelta:
    chapter_num: int
    new_arguments: list = field(default_factory=list)
    closed_arguments: list = field(default_factory=list)
    new_evidence: list = field(default_factory=list)
    evidence_gaps: list = field(default_factory=list)
    hook_updates: list = field(default_factory=list)
    character_updates: list = field(default_factory=list)
    chapter_summary: Optional[ChapterSummary] = None
    reader_journey_update: dict = field(default_factory=dict)


@dataclass
class ContextSection:
    category: str
    source: str
    reason: str
    summary: str
    content: str
    tokens: int


@dataclass
class ContextPack:
    sections: list = field(default_factory=list)
    total_tokens: int = 0
    budget_report: str = ""

    def to_dict(self) -> dict:
        return {
            "sections": [
                {
                    "category": s.category,
                    "source": s.source,
                    "reason": s.reason,
                    "summary": s.summary,
                    "tokens": s.tokens,
                }
                for s in self.sections
            ],
            "total_tokens": self.total_tokens,
            "budget_report": self.budget_report,
        }


@dataclass
class HookRef:
    hook_id: str
    action: str


@dataclass
class MemoConstraints:
    forbidden_patterns: list = field(default_factory=list)
    word_target: int = 3000
    style_rules: list = field(default_factory=list)
    pov_filter: list = field(default_factory=list)


@dataclass
class ChapterMemo:
    chapter_num: int
    goal: str
    opening: str
    middle: str
    climax: str
    ending: str
    hooks: list = field(default_factory=list)
    constraints: MemoConstraints = field(default_factory=MemoConstraints)


@dataclass
class RuleViolation:
    rule_id: str
    level: str
    description: str
    position: str
    snippet: str


@dataclass
class StyleFingerprint:
    avg_sentence_len: float
    median_sentence_len: float
    std_sentence_len: float
    p10_sentence_len: float
    p90_sentence_len: float
    avg_paragraph_len: float
    median_paragraph_len: float
    ttr: float
    top_sentence_starters: list = field(default_factory=list)
    rhetoric_density: dict = field(default_factory=dict)
    paragraph_type_ratio: dict = field(default_factory=dict)
