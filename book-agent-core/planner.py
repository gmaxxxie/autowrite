import os
from typing import Optional

from book_agent_core.models import ContextPack, ChapterMemo, MemoConstraints, HookRef


class Planner:
    def __init__(self, book_dir: str):
        self.book_dir = book_dir
        self.truth_dir = os.path.join(book_dir, "truth")
        self.runtime_dir = os.path.join(self.truth_dir, "runtime")
        self.index_dir = os.path.join(book_dir, "00-index")

    def _read_file(self, path: str) -> str:
        if not os.path.isfile(path):
            return ""
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()

    def _load_chapter_outline(self, chapter_num: int) -> str:
        bs = self._read_file(os.path.join(self.index_dir, "book-structure.md"))
        ch_tag = f"ch{chapter_num:02d}"
        if ch_tag in bs:
            idx = bs.index(ch_tag)
            section = bs[idx:idx+500]
            next_h = section.find("\n## ")
            if next_h > 0:
                section = section[:next_h]
            return section
        return ""

    def _load_active_hooks(self, chapter_num: int) -> list:
        import re
        hook_ledger = self._read_file(os.path.join(self.truth_dir, "hook_ledger.md"))
        hooks = []
        for m in re.finditer(r'\|\s*(H\d+)\s*\|\s*(\w+)\s*\|\s*([^|]+)\s*\|\s*(ch\d+)\s*\|\s*(ch\d+|TBD)\s*\|\s*(\w+)', hook_ledger):
            hook_id, htype, desc, seeded, payoff, status = m.groups()
            if status in ("seed", "planted", "progressing"):
                ch_num = int(re.search(r'ch(\d+)', payoff).group(1)) if re.search(r'ch(\d+)', payoff) else 999
                action = "resolve" if ch_num <= chapter_num else "advance"
                hooks.append(HookRef(hook_id=hook_id, action=action))
        return hooks

    def _load_forbidden_patterns(self) -> list:
        style = self._read_file(os.path.join(self.index_dir, "style-composition.md"))
        patterns = []
        if "首先其次最后" in style or True:
            patterns = [
                "首先...其次...最后...",
                "我们要...",
                "综上所述1.2.3.",
            ]
        return patterns

    def generate_memo(self, chapter_num: int, context_pack: ContextPack) -> ChapterMemo:
        ch_tag = f"ch{chapter_num:02d}"
        outline = self._load_chapter_outline(chapter_num)
        current_state = self._read_file(os.path.join(self.truth_dir, "current_state.md"))
        arg_state = self._read_file(os.path.join(self.truth_dir, "argument_state.md"))
        char_board = self._read_file(os.path.join(self.truth_dir, "character_board.md"))

        goal = self._derive_goal(outline, current_state)
        opening = self._derive_opening(outline, current_state)
        middle = self._derive_middle(outline, arg_state)
        climax = self._derive_climax(outline)
        ending = self._derive_ending(outline)
        hooks = self._load_active_hooks(chapter_num)
        constraints = MemoConstraints(
            forbidden_patterns=self._load_forbidden_patterns(),
            word_target=3000,
            style_rules=["过来人语调", "无机械枚举", "结尾非总结列表"],
            pov_filter=self._derive_pov_filter(char_board),
        )

        return ChapterMemo(
            chapter_num=chapter_num,
            goal=goal,
            opening=opening,
            middle=middle,
            climax=climax,
            ending=ending,
            hooks=hooks,
            constraints=constraints,
        )

    def _derive_goal(self, outline: str, state: str) -> str:
        import re
        m = re.search(r'目标[：:]\s*([^\n]+)', outline)
        if m:
            return m.group(1).strip()
        return "推进核心论点，承上启下"

    def _derive_opening(self, outline: str, state: str) -> str:
        import re
        m = re.search(r'标题[：:]\s*([^\n]+)', outline)
        title = m.group(1).strip() if m else ""
        if state:
            return f"承接上一章结论，以问题或悖论开篇引入「{title}」"
        return f"以具体场景或反直觉事实开篇，引出「{title}」"

    def _derive_middle(self, outline: str, arg_state: str) -> str:
        return "核心论证路径：提出问题→分析机制→给出框架→案例验证"

    def _derive_climax(self, outline: str) -> str:
        return "关键洞察或框架的顿悟时刻"

    def _derive_ending(self, outline: str) -> str:
        return "以未解决的问题或下一章预告收尾，种下新伏笔"

    def _derive_pov_filter(self, char_board: str) -> list:
        import re
        povs = []
        for m in re.finditer(r'\|\s*(\w+)\s*\|\s*([^|]+)\s*\|\s*expert_voice', char_board):
            povs.append(m.group(2).strip())
        return povs

    def save_memo(self, memo: ChapterMemo) -> str:
        os.makedirs(self.runtime_dir, exist_ok=True)
        out_path = os.path.join(self.runtime_dir, f"ch{memo.chapter_num:02d}_memo.md")
        lines = [
            f"# Chapter Memo: ch{memo.chapter_num:02d}",
            "",
            f"## Goal",
            memo.goal,
            "",
            f"## Opening",
            memo.opening,
            "",
            f"## Middle",
            memo.middle,
            "",
            f"## Climax",
            memo.climax,
            "",
            f"## Ending",
            memo.ending,
            "",
            f"## Hooks",
        ]
        for h in memo.hooks:
            lines.append(f"- {h.hook_id}: {h.action}")
        if not memo.hooks:
            lines.append("- (无活跃伏笔)")
        lines.append("")
        lines.append("## Constraints")
        lines.append(f"- 字数目标: {memo.constraints.word_target}")
        for p in memo.constraints.forbidden_patterns:
            lines.append(f"- 禁句: {p}")
        for r in memo.constraints.style_rules:
            lines.append(f"- 风格: {r}")
        for p in memo.constraints.pov_filter:
            lines.append(f"- POV: {p}")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return out_path
