#!/usr/bin/env python3
"""
autowrite-write-pipeline: 独立写章管道
由 autowrite-write 调用，或直接运行:
  python3 autowrite-write-pipeline.py next <书名> [--context "..."]
  python3 autowrite-write-pipeline.py exec <task_file>
"""
import os, sys, json, subprocess, argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

BOOKS_DIR = os.environ.get('BOOKS_DIR', os.path.join(os.path.expanduser('~'), 'books'))
PIPELINE_DIR = os.environ.get('PIPELINE_DIR', os.path.expanduser('~/.local/share/autowrite-pipeline'))

def find_book_dir(name):
    path = os.path.join(BOOKS_DIR, name)
    if os.path.isdir(path):
        return path
    # 向上查找
    cwd = os.getcwd()
    while cwd != '/':
        if os.path.isfile(os.path.join(cwd, 'book.conf')):
            return cwd
        cwd = os.path.dirname(cwd)
    return None

def detect_draft_dir(book_dir):
    book_name = os.path.basename(book_dir)
    candidates = [
        os.path.join(book_dir, '05-章节草稿', 'CN'),
        os.path.join(book_dir, '05-章节草稿', 'EN'),
        os.path.join(book_dir, '05-章节草稿'),
        os.path.join(book_dir, '05-chapter-drafts'),
        os.path.join(book_dir, '04-章节草稿', 'CN'),
    ]
    for d in candidates:
        if os.path.isdir(d):
            return d
    fallback = os.path.join(book_dir, '05-章节草稿', 'CN')
    os.makedirs(fallback, exist_ok=True)
    return fallback

def get_next_chapter(book_dir):
    summary_path = os.path.join(book_dir, 'truth', 'chapter_summaries.md')
    if os.path.isfile(summary_path):
        with open(summary_path) as f:
            content = f.read()
        # 找到 ## 当前章节 部分的 - 章节: chN
        import re
        m = re.search(r'^## 当前章节$.*?^- 章节: (ch\d+)', content, re.MULTILINE | re.DOTALL)
        if m:
            ch_num = int(m.group(1).replace('ch', ''))
            return ch_num + 1
    
    # fallback: book.conf
    conf_path = os.path.join(book_dir, 'book.conf')
    if os.path.isfile(conf_path):
        with open(conf_path) as f:
            for line in f:
                if line.startswith('CURRENT_CHAPTER='):
                    return int(line.split('=')[1].strip()) + 1
    return 1

def read_file(path, limit=3000):
    if not os.path.isfile(path):
        return ''
    with open(path, errors='replace') as f:
        return f.read()[:limit]

def cmd_next(book_name, user_context=''):
    book_dir = find_book_dir(book_name)
    if not book_dir:
        print(f"[✗] 找不到书籍: {book_name}", file=sys.stderr)
        sys.exit(1)
    
    draft_dir = detect_draft_dir(book_dir)
    truth_dir = os.path.join(book_dir, 'truth')
    next_ch = get_next_chapter(book_dir)
    
    os.makedirs(PIPELINE_DIR, exist_ok=True)
    task_id = f"task-{os.getpid()}"
    task_file = os.path.join(PIPELINE_DIR, f"{task_id}.json")
    
    # 读 book.conf
    book_conf = {}
    conf_path = os.path.join(book_dir, 'book.conf')
    if os.path.isfile(conf_path):
        with open(conf_path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    book_conf[k.strip()] = v
    
    # 收集概念卡
    concept_cards = []
    for concept_dir_name in ['02-概念卡', '02-concept-cards']:
        concept_dir = os.path.join(book_dir, concept_dir_name)
        if os.path.isdir(concept_dir):
            for card in sorted(os.listdir(concept_dir))[:5]:
                path = os.path.join(concept_dir, card)
                if os.path.isfile(path) and card.endswith('.md') and '索引' not in card and 'index' not in card.lower():
                    with open(path, errors='replace') as f:
                        content = f.read()[:1000]
                    concept_cards.append({'name': card[:-3], 'content': content})
            break

    cases = []
    for case_dir_name in ['03-案例库', '04-case-bank']:
        case_dir = os.path.join(book_dir, case_dir_name)
        if os.path.isdir(case_dir):
            for case in sorted(os.listdir(case_dir))[:5]:
                path = os.path.join(case_dir, case)
                if os.path.isfile(path) and case.endswith('.md'):
                    with open(path, errors='replace') as f:
                        content = f.read()[:1000]
                    cases.append({'name': case[:-3], 'content': content})
            break
    
    # 构建任务
    try:
        from book_agent_core import Composer, Planner

        composer = Composer(book_dir)
        context_pack = composer.compose(next_ch)
        context_pack_path = composer.save_context_pack(context_pack, next_ch)

        planner = Planner(book_dir)
        chapter_memo = planner.generate_memo(next_ch, context_pack)
        memo_path = planner.save_memo(chapter_memo)

        task = {
            'task_id': task_id,
            'book_dir': book_dir,
            'book_name': book_name,
            'draft_dir': draft_dir,
            'truth_dir': truth_dir,
            'next_chapter': str(next_ch),
            'user_context': user_context,
            'book_conf': {
                'book_name': book_conf.get('BOOK_NAME', book_name),
                'genre': book_conf.get('GENRE', 'non-fiction'),
                'chapter_target': int(book_conf.get('CHAPTER_TARGET', 0)),
                'current_chapter': int(book_conf.get('CURRENT_CHAPTER', 0)),
            },
            'context_pack': context_pack.to_dict(),
            'context_pack_path': context_pack_path,
            'chapter_memo_path': memo_path,
            'chapter_memo': {
                'goal': chapter_memo.goal,
                'opening': chapter_memo.opening,
                'middle': chapter_memo.middle,
                'climax': chapter_memo.climax,
                'ending': chapter_memo.ending,
                'hooks': [{'hook_id': h.hook_id, 'action': h.action} for h in chapter_memo.hooks],
                'constraints': {
                    'forbidden_patterns': chapter_memo.constraints.forbidden_patterns,
                    'word_target': chapter_memo.constraints.word_target,
                    'style_rules': chapter_memo.constraints.style_rules,
                },
            },
            'style_constraints': [
                '过来人掏心窝子，不苦口婆心，直接给判断',
                '无机械枚举（首先/其次/最后）',
                '无说教语气（我们要/我们应该）',
                '结尾不是总结列表，是问题/反思/钩子',
                '有类比或隐喻承载逻辑',
            ],
            'output_file': os.path.join(draft_dir, f'ch{next_ch:02d}.md'),
        }
    except (ImportError, Exception):
        task = {
            'task_id': task_id,
            'book_dir': book_dir,
            'book_name': book_name,
            'draft_dir': draft_dir,
            'truth_dir': truth_dir,
            'next_chapter': str(next_ch),
            'user_context': user_context,
            'book_conf': {
                'book_name': book_conf.get('BOOK_NAME', book_name),
                'genre': book_conf.get('GENRE', 'non-fiction'),
                'chapter_target': int(book_conf.get('CHAPTER_TARGET', 0)),
                'current_chapter': int(book_conf.get('CURRENT_CHAPTER', 0)),
            },
            'materials': {
                'argument_state': read_file(os.path.join(truth_dir, 'argument_state.md'), 4000),
                'chapter_summaries': read_file(os.path.join(truth_dir, 'chapter_summaries.md'), 4000),
                'evidence_ledger': read_file(os.path.join(truth_dir, 'evidence_ledger.md'), 4000),
                'open_questions': read_file(os.path.join(truth_dir, 'open_questions.md'), 2000),
            },
            'concept_cards': concept_cards,
            'cases': cases,
            'style_constraints': [
                '过来人掏心窝子，不苦口婆心，直接给判断',
                '无机械枚举（首先/其次/最后）',
                '无说教语气（我们要/我们应该）',
                '结尾不是总结列表，是问题/反思/钩子',
                '有类比或隐喻承载逻辑',
            ],
            'output_file': os.path.join(draft_dir, f'ch{next_ch:02d}.md'),
        }
    
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    
    print(f"[✓] 任务文件已生成: {task_file}", file=sys.stderr)
    print(f"书名: {book_name}")
    print(f"章节: ch{next_ch:02d}")
    print(f"输出: {task['output_file']}")
    print()
    print("执行方式:")
    print(f"  python3 {__file__} exec {task_file}")
    print()
    print("或对 Hermes agent 说:")
    print(f"  写 {book_name} 的第 {next_ch} 章")

def cmd_exec(task_file_path):
    """更新任务状态为 ready，输出 Hermes agent 执行指令。"""
    if not os.path.isfile(task_file_path):
        print(f"[✗] 任务文件不存在: {task_file_path}", file=sys.stderr)
        sys.exit(1)

    with open(task_file_path) as f:
        task = json.load(f)

    task['status'] = 'ready'
    with open(task_file_path, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)

    book_name = task['book_name']
    next_ch = task['next_chapter']
    task_id = task['task_id']
    output_file = task.get('output_file', '')

    print()
    print(f"━━━━━━━━━━━━━━━━━━━━")
    print(f"  任务已就绪")
    print(f"  书名: {book_name}")
    print(f"  章节: ch{int(next_ch):02d}")
    print(f"  ID:   {task_id}")
    print(f"  输出: {output_file}")
    print(f"━━━━━━━━━━━━━━━━━━━━")
    print()
    print("请对 Hermes agent 说:")
    print(f"  写 {book_name} 的第 {next_ch} 章")
    print()
    print("Hermes 将执行 $book-chapter-writer，自动完成:")
    print("  1. 写初稿 → 2. auto-revisor → 3. quality-audit → 4. 更新 truth/")
    print()

def main():
    parser = argparse.ArgumentParser(description='AutoWriteO 写章管道')
    parser.add_argument('command', choices=['next', 'exec', 'list', '_next_ch'])
    parser.add_argument('arg', nargs='?', help='书名 或 任务文件路径')
    parser.add_argument('--context', '-c', default='', help='额外上下文')
    
    args = parser.parse_args(sys.argv[1:] if len(sys.argv) > 1 else ['next'])
    
    if args.command == 'next':
        if not args.arg:
            print("[✗] 请提供书名", file=sys.stderr)
            sys.exit(1)
        cmd_next(args.arg, args.context)
    elif args.command == 'exec':
        if not args.arg:
            print("[✗] 请提供任务文件路径", file=sys.stderr)
            sys.exit(1)
        cmd_exec(args.arg)
    elif args.command == 'list':
        if not os.path.isdir(PIPELINE_DIR):
            print("暂无任务")
            return
        for f in sorted(os.listdir(PIPELINE_DIR)):
            if f.endswith('.json'):
                path = os.path.join(PIPELINE_DIR, f)
                with open(path) as fp:
                    t = json.load(fp)
                status = t.get('status', 'pending')
                print(f"  {t['task_id']}: {t['book_name']} ch{t['next_chapter']} — {status}")
    elif args.command == '_next_ch':
        if not args.arg:
            sys.exit(1)
        book_dir = find_book_dir(args.arg)
        if not book_dir:
            sys.exit(1)
        print(get_next_chapter(book_dir))

if __name__ == '__main__':
    main()
