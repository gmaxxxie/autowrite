import os
import re
from datetime import datetime
from typing import Optional

from book_agent_core.models import StateDelta, ChapterSummary


class Settler:
    def __init__(self, book_dir: str):
        self.book_dir = book_dir
        self.truth_dir = os.path.join(book_dir, "truth")
        self.runtime_dir = os.path.join(self.truth_dir, "runtime")
        os.makedirs(self.truth_dir, exist_ok=True)
        os.makedirs(self.runtime_dir, exist_ok=True)

    def _read_file(self, path: str) -> str:
        if not os.path.isfile(path):
            return ""
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()

    def _append_to_file(self, path: str, content: str):
        existing = self._read_file(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(existing.rstrip() + "\n" + content + "\n")

    def extract(self, chapter_text: str, chapter_num: int) -> StateDelta:
        ch_tag = f"ch{chapter_num:02d}"
        word_count = len(chapter_text.replace(" ", "").replace("\n", ""))

        new_arguments = self._extract_arguments(chapter_text, ch_tag)
        new_evidence = self._extract_evidence(chapter_text, ch_tag)
        hook_updates = self._extract_hook_updates(chapter_text, ch_tag)
        char_updates = self._extract_character_updates(chapter_text, ch_tag)

        title_match = re.search(r'^#\s+(.+)', chapter_text)
        title = title_match.group(1).strip() if title_match else f"第{chapter_num}章"

        core_arg = new_arguments[0].statement if new_arguments else ""
        key_cases = [e.description for e in new_evidence if e.ev_type == "case"]

        delta = StateDelta(
            chapter_num=chapter_num,
            new_arguments=new_arguments,
            closed_arguments=[],
            new_evidence=new_evidence,
            evidence_gaps=[],
            hook_updates=hook_updates,
            character_updates=char_updates,
            chapter_summary=ChapterSummary(
                chapter=ch_tag,
                title=title,
                word_count=word_count,
                core_argument=core_arg,
                key_cases=key_cases[:3],
                foreshadowing=[h.hook_id for h in hook_updates if h.new_status in ("seed", "planted")],
            ),
            reader_journey_update={
                "chapter": ch_tag,
                "pace": "medium",
                "emotion": "engaged",
                "density": "high",
            },
        )
        return delta

    def _extract_arguments(self, text: str, ch_tag: str) -> list:
        from book_agent_core.models import Argument
        args = []
        patterns = [
            r'核心论点[是为：:]\s*([^\n。，]+)',
            r'关键(?:洞察|发现)[是为：:]\s*([^\n。，]+)',
        ]
        for pat in patterns:
            for m in re.finditer(pat, text):
                args.append(Argument(
                    arg_id=f"A{len(args)+1:03d}",
                    statement=m.group(1).strip(),
                    chapter_introduced=ch_tag,
                    status="in-progress",
                ))
        return args

    def _extract_evidence(self, text: str, ch_tag: str) -> list:
        from book_agent_core.models import Evidence
        evs = []
        case_pattern = r'案例[：:]\s*([^\n。，]+)'
        for m in re.finditer(case_pattern, text):
            evs.append(Evidence(
                ev_id=f"C{len(evs)+1:03d}",
                ev_type="case",
                description=m.group(1).strip(),
                source="",
                reliability="unverified",
                chapter_used=ch_tag,
            ))
        data_pattern = r'根据([^\n，]{2,30}?)(?:报告|研究|数据|调查)[，,]\s*(\d+[%％]|\d+[万亿千百]+)'
        for m in re.finditer(data_pattern, text):
            evs.append(Evidence(
                ev_id=f"D{len(evs)+1:03d}",
                ev_type="data",
                description=f"{m.group(2)} (来源: {m.group(1).strip()})",
                source=m.group(1).strip(),
                reliability="unverified",
                chapter_used=ch_tag,
            ))
        return evs

    def _extract_hook_updates(self, text: str, ch_tag: str) -> list:
        from book_agent_core.models import HookDelta
        updates = []
        foreshadow_pattern = r'伏笔[：:]\s*([^\n]+)'
        for m in re.finditer(foreshadow_pattern, text):
            updates.append(HookDelta(
                hook_id=f"H{len(updates)+1:03d}",
                old_status="",
                new_status="seed",
                reason=m.group(1).strip(),
            ))
        resolve_pattern = r'(?:呼应|回应|解答|解决)[了]?[了：:]\s*([^\n]+)'
        for m in re.finditer(resolve_pattern, text):
            updates.append(HookDelta(
                hook_id=f"H{len(updates)+1:03d}",
                old_status="progressing",
                new_status="resolved",
                reason=m.group(1).strip(),
            ))
        return updates

    def _extract_character_updates(self, text: str, ch_tag: str) -> list:
        from book_agent_core.models import CharDelta
        return []

    def apply_delta(self, delta: StateDelta):
        ch_tag = f"ch{delta.chapter_num:02d}"

        if delta.chapter_summary:
            self._update_chapter_summaries(delta.chapter_summary)
            self._update_current_state(delta)
            self._update_reader_journey(delta)

        if delta.new_arguments:
            self._update_argument_state(delta.new_arguments, ch_tag)

        if delta.new_evidence:
            self._update_evidence_ledger(delta.new_evidence, ch_tag)

        if delta.hook_updates:
            self._update_hook_ledger(delta.hook_updates, ch_tag)

        self._append_settler_log(delta)

    def _update_chapter_summaries(self, summary: ChapterSummary):
        path = os.path.join(self.truth_dir, "chapter_summaries.md")
        existing = self._read_file(path)
        row = f"| {summary.chapter} | {summary.title} | {summary.word_count} | {summary.core_argument} | {', '.join(summary.key_cases[:3])} | {', '.join(summary.foreshadowing[:3])} |"
        if summary.chapter in existing:
            lines = existing.split("\n")
            new_lines = []
            for line in lines:
                if line.startswith(f"| {summary.chapter} "):
                    new_lines.append(row)
                else:
                    new_lines.append(line)
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
        else:
            self._append_to_file(path, row)

    def _update_argument_state(self, arguments: list, ch_tag: str):
        path = os.path.join(self.truth_dir, "argument_state.md")
        existing = self._read_file(path)
        for arg in arguments:
            if arg.arg_id not in existing:
                row = f"| {ch_tag} | {arg.statement} | [ ] {arg.status} |"
                self._append_to_file(path, row)

    def _update_evidence_ledger(self, evidences: list, ch_tag: str):
        path = os.path.join(self.truth_dir, "evidence_ledger.md")
        existing = self._read_file(path)
        for ev in evidences:
            if ev.ev_id not in existing:
                row = f"| {ev.ev_id} | {ev.description} | {ev.ev_type} | {ch_tag} | {ev.reliability} |"
                self._append_to_file(path, row)

    def _update_hook_ledger(self, hook_updates: list, ch_tag: str):
        path = os.path.join(self.truth_dir, "hook_ledger.md")
        if not os.path.isfile(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("## 伏笔账本\n\n| ID | 类型 | 描述 | 种下章节 | 预期解决 | 状态 | 健康度 |\n|----|------|------|---------|---------|------|--------|\n")
        for hu in hook_updates:
            row = f"| {hu.hook_id} | auto | {hu.reason} | {ch_tag} | TBD | {hu.new_status} | on-track |"
            self._append_to_file(path, row)

    def _update_reader_journey(self, delta: StateDelta):
        path = os.path.join(self.truth_dir, "reader_journey.md")
        rj = delta.reader_journey_update
        if rj:
            row = f"| {rj.get('chapter', '')} | {rj.get('pace', '')} | {rj.get('emotion', '')} | {rj.get('density', '')} |"
            self._append_to_file(path, row)

    def _update_current_state(self, delta: StateDelta):
        path = os.path.join(self.truth_dir, "current_state.md")
        ch_tag = f"ch{delta.chapter_num:02d}"
        summary = delta.chapter_summary
        lines = [
            f"# 当前状态 (Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')})",
            "",
            f"## 最新完成章节",
            f"- 章节: {ch_tag}",
            f"- 标题: {summary.title if summary else ''}",
            f"- 字数: {summary.word_count if summary else 0}",
            f"- 核心论点: {summary.core_argument if summary else ''}",
            "",
            f"## 进行中的论点",
        ]
        for arg in delta.new_arguments:
            lines.append(f"- {arg.arg_id}: {arg.statement} ({arg.status})")
        if not delta.new_arguments:
            lines.append("- (无新增)")
        lines.append("")
        lines.append("## 待解决的伏笔")
        for hu in delta.hook_updates:
            if hu.new_status != "resolved":
                lines.append(f"- {hu.hook_id}: {hu.reason} ({hu.new_status})")
        if not any(hu.new_status != "resolved" for hu in delta.hook_updates):
            lines.append("- (无)")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _append_settler_log(self, delta: StateDelta):
        path = os.path.join(self.truth_dir, "settler_log.md")
        ch_tag = f"ch{delta.chapter_num:02d}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n### {timestamp} — {ch_tag} StateDelta\n"
        entry += f"- new_arguments: {len(delta.new_arguments)}\n"
        entry += f"- new_evidence: {len(delta.new_evidence)}\n"
        entry += f"- hook_updates: {len(delta.hook_updates)}\n"
        entry += f"- character_updates: {len(delta.character_updates)}\n"
        self._append_to_file(path, entry)
