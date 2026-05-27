import json
import os
import re
from typing import Optional

from book_agent_core.models import RuleViolation


RULES = [
    {
        "id": "R01",
        "name": "禁句模式",
        "level": "阻断",
        "patterns": [
            r'(?:首先|第一)[，,].{0,30}(?:其次|第二)[，,].{0,30}(?:最后|第三)',
            r'我们要\S{2,10}',
        ],
        "description": "机械枚举或说教句式",
    },
    {
        "id": "R02",
        "name": "AI标记密度",
        "level": "警告",
        "patterns": [],
        "keyword_groups": [
            ["值得注意的是", "总的来说", "毋庸置疑", "显而易见", "众所周知", "不可否认", "总而言之", "综上所述", "事实上", "实际上"],
        ],
        "threshold": 3,
        "description": "AI典型表达密度过高",
    },
    {
        "id": "R03",
        "name": "元叙述",
        "level": "警告",
        "patterns": [],
        "count_patterns": [r'如前所述', r'在上一章中', r'前面提到', r'正如我们讨论过的'],
        "count_threshold": 2,
        "description": "过度引用前文",
    },
    {
        "id": "R04",
        "name": "报告词无来源",
        "level": "警告",
        "patterns": [
            r'研究表明[，,]?\s*(?!\(|[（])',
            r'数据显示[，,]?\s*(?!\(|[（])',
        ],
        "description": "报告词后无来源标注",
    },
    {
        "id": "R05",
        "name": "作者说教",
        "level": "警告",
        "patterns": [],
        "count_patterns": [r'我们必须', r'我们应该', r'你要明白', r'让我们', r'你一定要', r'务必'],
        "count_threshold": 3,
        "description": "祈使句密度过高",
    },
    {
        "id": "R06",
        "name": "集体震惊",
        "level": "阻断",
        "patterns": [
            r'震惊了所有人',
            r'颠覆了认知',
            r'彻底改变了.{0,10}格局',
            r'前所未有地.{0,6}震惊',
        ],
        "description": "夸大集体反应",
    },
    {
        "id": "R07",
        "name": "跨章首尾重复",
        "level": "警告",
        "patterns": [],
        "description": "需跨章对比，此处仅标记提醒",
    },
    {
        "id": "R08",
        "name": "数据无来源",
        "level": "阻断",
        "patterns": [
            r'(?:增长|下降|提升|减少|达到|超过)了?\s*\d+[%％万亿千百]',
            r'\d+[万亿千百]+\s*(?:用户|人|企业|公司)',
            r'\$\s*\d+',
        ],
        "source_required": True,
        "description": "具体数字无来源",
    },
    {
        "id": "R09",
        "name": "敏感词",
        "level": "阻断",
        "patterns": [],
        "sensitive_words": {
            "阻断": [],
            "警告": [],
        },
        "description": "政治/色情/极端暴力词汇",
    },
]


class RuleEngine:
    def __init__(self, book_dir: Optional[str] = None):
        self.book_dir = book_dir
        self._load_sensitive_words()

    def _load_sensitive_words(self):
        if not self.book_dir:
            return
        sw_path = os.path.join(self.book_dir, "00-index", "sensitive_words.txt")
        if os.path.isfile(sw_path):
            with open(sw_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "|" in line:
                        level, word = line.split("|", 1)
                        if level in RULES[8]["sensitive_words"]:
                            RULES[8]["sensitive_words"][level].append(word)

    def check(self, text: str, prev_chapter_ending: str = "") -> list:
        violations = []
        for rule in RULES:
            rule_violations = self._check_rule(rule, text, prev_chapter_ending)
            violations.extend(rule_violations)
        return violations

    def _check_rule(self, rule: dict, text: str, prev_ending: str) -> list:
        violations = []
        rule_id = rule["id"]

        if rule_id == "R07":
            if prev_ending:
                overlap = self._compute_overlap(prev_ending, text[:200])
                if overlap > 0.6:
                    violations.append(RuleViolation(
                        rule_id=rule_id, level=rule["level"],
                        description=f"跨章首尾重复度 {overlap:.0%}",
                        position="章首", snippet=text[:50],
                    ))
            return violations

        if rule_id == "R09":
            for level, words in rule.get("sensitive_words", {}).items():
                for word in words:
                    if word in text:
                        violations.append(RuleViolation(
                            rule_id=rule_id, level=level,
                            description=f"敏感词: {word}",
                            position="全文", snippet=word,
                        ))
            return violations

        if rule.get("patterns"):
            for pat in rule["patterns"]:
                for m in re.finditer(pat, text):
                    snippet = m.group()[:30]
                    pos = self._find_position(text, m.start())
                    violations.append(RuleViolation(
                        rule_id=rule_id, level=rule["level"],
                        description=rule["description"],
                        position=pos, snippet=snippet,
                    ))

        if rule.get("keyword_groups"):
            for group in rule["keyword_groups"]:
                count = sum(1 for kw in group if kw in text)
                threshold = rule.get("threshold", 3)
                if count >= threshold:
                    violations.append(RuleViolation(
                        rule_id=rule_id, level=rule["level"],
                        description=f"{rule['description']} ({count}/{len(group)} 关键词)",
                        position="全文", snippet=", ".join(kw for kw in group if kw in text)[:50],
                    ))

        if rule.get("count_patterns"):
            count = sum(len(re.findall(p, text)) for p in rule["count_patterns"])
            threshold = rule.get("count_threshold", 2)
            if count >= threshold:
                violations.append(RuleViolation(
                    rule_id=rule_id, level=rule["level"],
                    description=f"{rule['description']} ({count}次)",
                    position="全文", snippet="",
                ))

        if rule.get("source_required") and rule.get("patterns"):
            for pat in rule["patterns"]:
                for m in re.finditer(pat, text):
                    after = text[m.end():m.end()+30]
                    if not re.search(r'[\(（\[【]', after):
                        snippet = m.group()[:30]
                        pos = self._find_position(text, m.start())
                        violations.append(RuleViolation(
                            rule_id=rule_id, level=rule["level"],
                            description=rule["description"],
                            position=pos, snippet=snippet,
                        ))

        return violations

    def _find_position(self, text: str, char_idx: int) -> str:
        before = text[:char_idx]
        paragraph = before.count("\n\n") + 1
        return f"第{paragraph}段"

    def _compute_overlap(self, text_a: str, text_b: str) -> float:
        set_a = set(text_a)
        set_b = set(text_b)
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)

    def save_report(self, violations: list, out_path: str):
        os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
        report = {
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "level": v.level,
                    "description": v.description,
                    "position": v.position,
                    "snippet": v.snippet,
                }
                for v in violations
            ],
            "total": len(violations),
            "blocked": any(v.level == "阻断" for v in violations),
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
