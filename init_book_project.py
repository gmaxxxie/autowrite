#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_SCRIPT = (
    REPO_ROOT
    / "book-writing-skills"
    / "skills"
    / "book-project-workspace"
    / "scripts"
    / "scaffold_book_project.py"
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize a new enhanced Obsidian + Codex book project.",
    )
    parser.add_argument("target_dir", help="Root directory for the new book project")
    parser.add_argument("--book-title", required=True, help="Primary working title")
    parser.add_argument("--book-title-en", default="TBD", help="English working title")
    parser.add_argument("--author", default="TBD", help="Author name")
    parser.add_argument("--chapter-dir", help="Folder name under 05-章节草稿/")
    parser.add_argument("--imprint", default="TBD", help="Publisher or imprint name")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing scaffold files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    parser.add_argument(
        "--git-init",
        action="store_true",
        help="Initialize a git repository in the target directory",
    )
    parser.add_argument(
        "--git-branch",
        default="main",
        help="Initial branch name when using --git-init",
    )
    return parser


def run_command(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    if not SCAFFOLD_SCRIPT.exists():
        parser.error(f"Scaffold script not found: {SCAFFOLD_SCRIPT}")

    target_dir = Path(args.target_dir).expanduser().resolve()

    command = [
        "python3",
        str(SCAFFOLD_SCRIPT),
        str(target_dir),
        "--book-title",
        args.book_title,
        "--book-title-en",
        args.book_title_en,
        "--author",
        args.author,
        "--imprint",
        args.imprint,
    ]

    if args.chapter_dir:
        command.extend(["--chapter-dir", args.chapter_dir])
    if args.overwrite:
        command.append("--overwrite")
    if args.dry_run:
        command.append("--dry-run")

    try:
        run_command(command)

        if args.git_init and not args.dry_run:
            run_command(["git", "init", "-b", args.git_branch], cwd=target_dir)
            print("")
            print(f"Initialized git repository on branch '{args.git_branch}'.")
            print(f"  {target_dir / '.git'}")
    except subprocess.CalledProcessError as exc:
        return exc.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
