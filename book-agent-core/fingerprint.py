import json
import os
import re
import statistics
from typing import Optional

from book_agent_core.models import StyleFingerprint


class FingerprintExtractor:
    def __init__(self, book_dir: str = ""):
        self.book_dir = book_dir
        self.index_dir = os.path.join(book_dir, "00-index")

    def _detect_draft_dir(self) -> str:
        for d in ["05-章节草稿/CN", "05-章节草稿/EN", "05-章节草稿", "05-chapter-drafts"]:
            full = os.path.join(self.book_dir, d)
            if os.path.isdir(full):
                return full
        return os.path.join(self.book_dir, "05-章节草稿", "CN")

    def _read_all_chapters(self) -> str:
        draft_dir = self._detect_draft_dir()
        texts = []
        if os.path.isdir(draft_dir):
            for fn in sorted(os.listdir(draft_dir)):
                if fn.endswith(".md") and fn.startswith("ch"):
                    fp = os.path.join(draft_dir, fn)
                    with open(fp, encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    if any(x in fn for x in ["tickets", "report", "auto-revisor", "quality", "de-ai"]):
                        continue
                    texts.append(content)
        return "\n\n".join(texts)

    def _split_sentences(self, text: str) -> list:
        text = re.sub(r'\n+', ' ', text)
        sents = re.split(r'[。！？；]', text)
        return [s.strip() for s in sents if len(s.strip()) > 1]

    def _split_paragraphs(self, text: str) -> list:
        paras = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paras if len(p.strip()) > 10]

    def sentence_lengths(self, text: str) -> dict:
        sents = self._split_sentences(text)
        lengths = [len(s) for s in sents if len(s) > 0]
        if not lengths:
            return {"avg": 0, "median": 0, "std": 0, "p10": 0, "p90": 0}
        sorted_l = sorted(lengths)
        n = len(sorted_l)
        p10_idx = max(0, int(n * 0.1))
        p90_idx = min(n - 1, int(n * 0.9))
        return {
            "avg": round(statistics.mean(lengths), 1),
            "median": round(statistics.median(lengths), 1),
            "std": round(statistics.stdev(lengths), 1) if len(lengths) > 1 else 0,
            "p10": sorted_l[p10_idx],
            "p90": sorted_l[p90_idx],
        }

    def paragraph_lengths(self, text: str) -> dict:
        paras = self._split_paragraphs(text)
        lengths = [len(p) for p in paras if len(p) > 0]
        if not lengths:
            return {"avg": 0, "median": 0}
        return {
            "avg": round(statistics.mean(lengths), 1),
            "median": round(statistics.median(lengths), 1),
        }

    def type_token_ratio(self, text: str) -> float:
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text)
        if not words:
            return 0.0
        tokens = []
        for w in words:
            if re.match(r'[\u4e00-\u9fff]+', w):
                tokens.extend(list(w))
            else:
                tokens.append(w.lower())
        types = set(tokens)
        return round(len(types) / len(tokens), 3)

    def top_sentence_starters(self, text: str, top_n: int = 10) -> list:
        sents = self._split_sentences(text)
        starters = []
        for s in sents:
            first_chars = s[:2].strip() if len(s) >= 2 else s[:1].strip()
            if first_chars:
                starters.append(first_chars)
        if not starters:
            return []
        from collections import Counter
        counter = Counter(starters)
        return counter.most_common(top_n)

    def rhetoric_density(self, text: str) -> dict:
        patterns = {
            "类比": len(re.findall(r'(?:就像|好比|仿佛|宛如|如同)', text)),
            "隐喻": len(re.findall(r'(?:是|成了|变成)\s*[^。，\n]{2,8}的[^。，\n]{2,8}', text)),
            "反问": len(re.findall(r'[吗呢吧]\s*[？?]', text)),
            "排比": len(re.findall(r'(?:[\u4e00-\u9fff]{2,6}[，,]){2,}', text)),
        }
        total_chars = len(text.replace(" ", "").replace("\n", ""))
        if total_chars == 0:
            return patterns
        return {k: round(v / total_chars * 1000, 2) for k, v in patterns.items()}

    def paragraph_type_ratio(self, text: str) -> dict:
        paras = self._split_paragraphs(text)
        types = {"论证": 0, "叙述": 0, "案例": 0, "反思": 0}
        for p in paras:
            if re.search(r'(?:因此|所以|这意味着|这说明|核心是|关键是)', p):
                types["论证"] += 1
            elif re.search(r'(?:案例|故事|经历|曾经|有一次)', p):
                types["案例"] += 1
            elif re.search(r'(?:你可能会|也许|是否|会不会)', p):
                types["反思"] += 1
            else:
                types["叙述"] += 1
        total = sum(types.values())
        if total == 0:
            return types
        return {k: round(v / total, 2) for k, v in types.items()}

    def extract(self) -> StyleFingerprint:
        text = self._read_all_chapters()
        sl = self.sentence_lengths(text)
        pl = self.paragraph_lengths(text)
        return StyleFingerprint(
            avg_sentence_len=sl["avg"],
            median_sentence_len=sl["median"],
            std_sentence_len=sl["std"],
            p10_sentence_len=sl["p10"],
            p90_sentence_len=sl["p90"],
            avg_paragraph_len=pl["avg"],
            median_paragraph_len=pl["median"],
            ttr=self.type_token_ratio(text),
            top_sentence_starters=self.top_sentence_starters(text),
            rhetoric_density=self.rhetoric_density(text),
            paragraph_type_ratio=self.paragraph_type_ratio(text),
        )

    def save(self, fp: StyleFingerprint) -> str:
        os.makedirs(self.index_dir, exist_ok=True)
        out_path = os.path.join(self.index_dir, "style_fingerprint.json")
        data = {
            "avg_sentence_len": fp.avg_sentence_len,
            "median_sentence_len": fp.median_sentence_len,
            "std_sentence_len": fp.std_sentence_len,
            "p10_sentence_len": fp.p10_sentence_len,
            "p90_sentence_len": fp.p90_sentence_len,
            "avg_paragraph_len": fp.avg_paragraph_len,
            "median_paragraph_len": fp.median_paragraph_len,
            "ttr": fp.ttr,
            "top_sentence_starters": fp.top_sentence_starters,
            "rhetoric_density": fp.rhetoric_density,
            "paragraph_type_ratio": fp.paragraph_type_ratio,
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return out_path
