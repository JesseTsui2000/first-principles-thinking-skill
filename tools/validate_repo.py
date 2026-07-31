#!/usr/bin/env python3
"""Validate the repository without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "first-principles-thinking"
SKILL_FILE = ROOT / "skills" / SKILL_NAME / "SKILL.md"
EVAL_FILE = ROOT / "skills" / SKILL_NAME / "evals" / "evals.json"
EVAL_README_FILE = ROOT / "skills" / SKILL_NAME / "evals" / "README.md"
VERSION_FILE = ROOT / "VERSION"
README_FILE = ROOT / "README.md"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"

REQUIRED_FILES = [
    README_FILE,
    ROOT / "LICENSE",
    CHANGELOG_FILE,
    ROOT / "CONTRIBUTING.md",
    ROOT / "PUBLISHING.md",
    ROOT / "RELEASE_CHECKLIST.md",
    SKILL_FILE,
    EVAL_FILE,
    EVAL_README_FILE,
    VERSION_FILE,
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        fail("SKILL.md must begin with YAML frontmatter")

    end = text.find("\n---\n", 4)
    if end == -1:
        fail("SKILL.md frontmatter is not closed")

    block = text[4:end]
    result: dict[str, object] = {}
    metadata: dict[str, str] = {}
    in_metadata = False

    for raw_line in block.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if raw_line.startswith("  ") and in_metadata:
            key, sep, value = raw_line.strip().partition(":")
            if not sep:
                fail(f"invalid metadata line: {raw_line}")
            metadata[key.strip()] = value.strip().strip('"').strip("'")
            continue

        in_metadata = False
        key, sep, value = raw_line.partition(":")
        if not sep:
            fail(f"invalid frontmatter line: {raw_line}")

        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key == "metadata":
            in_metadata = True
            result["metadata"] = metadata
        else:
            result[key] = value

    return result


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")

    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail("VERSION must use MAJOR.MINOR.PATCH")

    readme_text = README_FILE.read_text(encoding="utf-8")
    if f"当前版本：`v{version}`" not in readme_text:
        fail(f"README.md must declare current version v{version}")

    changelog_text = CHANGELOG_FILE.read_text(encoding="utf-8")
    if not re.search(rf"^## \[{re.escape(version)}\](?:\s|$)", changelog_text, re.MULTILINE):
        fail(f"CHANGELOG.md must contain a ## [{version}] entry")

    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    fm = parse_frontmatter(skill_text)

    name = str(fm.get("name", ""))
    description = str(fm.get("description", ""))
    metadata = fm.get("metadata")

    if name != SKILL_NAME:
        fail("frontmatter name must match the parent directory")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        fail("skill name must contain lowercase letters, digits, and single hyphens only")
    if not 1 <= len(name) <= 64:
        fail("skill name length must be 1-64 characters")
    if not 1 <= len(description) <= 1024:
        fail("description length must be 1-1024 characters")
    if not isinstance(metadata, dict):
        fail("metadata must be present")
    if metadata.get("version") != version:
        fail("SKILL.md metadata.version must match VERSION")
    if not metadata.get("author"):
        fail("metadata.author is required for this repository")

    line_count = len(skill_text.splitlines())
    if line_count > 500:
        fail(f"SKILL.md has {line_count} lines; keep it at or below 500")

    try:
        eval_data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"evals.json is invalid JSON: {exc}")

    if eval_data.get("skill") != SKILL_NAME:
        fail("evals.json skill name does not match")
    if eval_data.get("version") != version:
        fail("evals.json version must match VERSION")

    cases = eval_data.get("cases")
    if not isinstance(cases, list) or len(cases) < 6:
        fail("evals.json must contain at least 6 cases")

    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            fail("each eval case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            fail("each eval case requires an id")
        if case_id in seen:
            fail(f"duplicate eval id: {case_id}")
        seen.add(case_id)
        for field in ("prompt", "should_activate", "expected_behaviors", "failure_signals"):
            if field not in case:
                fail(f"eval {case_id} missing field: {field}")
        if not isinstance(case["should_activate"], bool):
            fail(f"eval {case_id} should_activate must be boolean")
        if not case["expected_behaviors"] or not case["failure_signals"]:
            fail(f"eval {case_id} needs expected behaviors and failure signals")

    print(f"PASS: {SKILL_NAME} v{version}")
    print("PASS: README.md current version matches VERSION")
    print(f"PASS: CHANGELOG.md contains [{version}]")
    print("PASS: evals/README.md exists")
    print(f"PASS: {len(cases)} eval cases")
    print(f"PASS: SKILL.md has {line_count} lines")
    print("PASS: repository validation completed")


if __name__ == "__main__":
    main()
