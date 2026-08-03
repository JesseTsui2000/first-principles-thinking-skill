#!/usr/bin/env python3
"""Validate the repository without third-party dependencies."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath

import build_openai_plugin as plugin_builder

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "first-principles-thinking"
SKILL_FILE = ROOT / "skills" / SKILL_NAME / "SKILL.md"
EVAL_FILE = ROOT / "skills" / SKILL_NAME / "evals" / "evals.json"
EVAL_README_FILE = ROOT / "skills" / SKILL_NAME / "evals" / "README.md"
VERSION_FILE = ROOT / "VERSION"
PLUGIN_VERSION_FILE = ROOT / "PLUGIN_VERSION"
PLUGIN_MANIFEST_FILE = ROOT / "packaging" / "openai-plugin" / "plugin.json"
ROOT_PLUGIN_MANIFEST_FILE = ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE_FILE = ROOT / ".agents" / "plugins" / "marketplace.json"
SUBMISSION_TESTS_FILE = ROOT / "plugin-submission" / "test-cases.json"
OPENAI_PLUGIN_FILE = ROOT / "OPENAI_PLUGIN.md"
README_FILE = ROOT / "README.md"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
BUILD_SCRIPT_FILE = ROOT / "tools" / "build_openai_plugin.py"
GENERATED_PACKAGE_ROOT = ROOT / ".build" / "plugins" / SKILL_NAME
MARKETPLACE_SOURCE_PATH = "./.build/plugins/first-principles-thinking"

PLACEHOLDER_RE = re.compile(r"<[A-Z][A-Z0-9_-]*>")
PROHIBITED_PLUGIN_FIELDS = {"mcpServers", "apps", "hooks"}
COMMON_SUBMISSION_STRING_FIELDS = ("id", "type", "user_prompt", "fixture", "source_eval_id")
POSITIVE_STRING_ARRAY_FIELDS = ("expected_behavior", "expected_result_shape")
NEGATIVE_STRING_FIELDS = ("expected_fallback", "reason_not_to_complete")
FALLBACK_SKILL_SCAN_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".build",
    "dist",
    "build",
}

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
    PLUGIN_VERSION_FILE,
    PLUGIN_MANIFEST_FILE,
    MARKETPLACE_FILE,
    SUBMISSION_TESTS_FILE,
    OPENAI_PLUGIN_FILE,
    BUILD_SCRIPT_FILE,
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


def load_json_object(path: Path, label: str) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{label} is invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{label} must contain a JSON object")
    return data


def path_exists(path: Path) -> bool:
    return os.path.lexists(path)


def validate_generated_git_state() -> None:
    if not (ROOT / ".git").exists():
        ignore_lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if ".build/" not in (line.strip() for line in ignore_lines):
            fail(".build/ must be ignored")
        return

    try:
        ignored = subprocess.run(
            [
                "git",
                "-C",
                str(ROOT),
                "check-ignore",
                "-q",
                "--no-index",
                ".build/plugins/first-principles-thinking/probe",
            ],
            check=False,
        )
    except FileNotFoundError:
        fail("git is required to validate ignored and tracked generated output")
    else:
        if ignored.returncode != 0:
            fail(".build/ must be ignored")

    try:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z", "--", ".build"],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        fail("git is required to validate ignored and tracked generated output")
    except subprocess.CalledProcessError as exc:
        fail(f"unable to inspect tracked .build files: {exc}")
    if tracked.stdout:
        paths = tracked.stdout.decode("utf-8", errors="surrogateescape").split("\0")
        fail(f".build must not contain tracked files: {', '.join(filter(None, paths))}")


def validate_marketplace_path(raw_path: object) -> Path:
    if raw_path != MARKETPLACE_SOURCE_PATH:
        fail(f"marketplace source.path must be exactly {MARKETPLACE_SOURCE_PATH}")
    if not isinstance(raw_path, str) or not raw_path.startswith("./"):
        fail("marketplace source.path must be a relative path beginning with ./")
    pure_path = PurePosixPath(raw_path)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        fail("marketplace source.path must not be absolute or contain ..")
    resolved = (ROOT / raw_path).resolve(strict=False)
    expected = GENERATED_PACKAGE_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        fail("marketplace source.path must remain inside the marketplace root")
    if resolved == ROOT.resolve():
        fail("marketplace source.path must not point to the repository root")
    if resolved != expected:
        fail("marketplace source.path must resolve to the fixed generated Plugin root")
    return resolved


def json_type_name(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return type(value).__name__


def require_non_empty_string(case: dict[str, object], field: str, case_id: str) -> str:
    if field not in case:
        fail(
            f"submission test {case_id} field {field} must be a non-empty string; "
            "actual: missing"
        )
    value = case[field]
    if not isinstance(value, str):
        fail(
            f"submission test {case_id} field {field} must be a non-empty string; "
            f"actual type: {json_type_name(value)}"
        )
    if not value.strip():
        fail(
            f"submission test {case_id} field {field} must be a non-empty string; "
            "actual: empty string"
        )
    return value


def require_non_empty_string_array(
    case: dict[str, object], field: str, case_id: str
) -> list[str]:
    if field not in case:
        fail(
            f"submission test {case_id} field {field} must be a non-empty array "
            "of non-empty strings; actual: missing"
        )
    value = case[field]
    if not isinstance(value, list):
        fail(
            f"submission test {case_id} field {field} must be a non-empty array "
            f"of non-empty strings; actual type: {json_type_name(value)}"
        )
    if not value:
        fail(
            f"submission test {case_id} field {field} must be a non-empty array "
            "of non-empty strings; actual: empty array"
        )
    for item_index, item in enumerate(value):
        if not isinstance(item, str):
            fail(
                f"submission test {case_id} field {field}[{item_index}] must be "
                f"a non-empty string; actual type: {json_type_name(item)}"
            )
        if not item.strip():
            fail(
                f"submission test {case_id} field {field}[{item_index}] must be "
                "a non-empty string; actual: empty string"
            )
    return value


def repository_skill_files() -> list[str]:
    git_metadata = ROOT / ".git"
    if git_metadata.exists():
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(ROOT),
                    "ls-files",
                    "-z",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                ],
                check=True,
                capture_output=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        else:
            paths = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
            return sorted(path for path in paths if Path(path).name == "SKILL.md")

    skill_files: list[str] = []
    for current_root, directory_names, file_names in os.walk(ROOT, followlinks=False):
        directory_names[:] = sorted(
            directory_name
            for directory_name in directory_names
            if directory_name not in FALLBACK_SKILL_SCAN_EXCLUDED_DIRS
        )
        if "SKILL.md" in file_names:
            path = Path(current_root) / "SKILL.md"
            skill_files.append(path.relative_to(ROOT).as_posix())
    return sorted(skill_files)


def validate_plugin(version: str) -> tuple[str, int, int, bool]:
    try:
        source_state = plugin_builder.validate_sources()
        plugin_builder.validate_output_location()
    except plugin_builder.BuildError as exc:
        fail(str(exc))
    plugin_version = source_state.plugin_version
    if not plugin_builder.is_strict_three_part_version(plugin_version):
        fail("PLUGIN_VERSION must use MAJOR.MINOR.PATCH")
    if source_state.core_version != version:
        fail("builder source validation Core Skill version must match VERSION")

    lowercase_category_manifest = dict(source_state.manifest)
    interface = lowercase_category_manifest.get("interface")
    if not isinstance(interface, dict):
        fail("canonical manifest interface must be an object")
    lowercase_category_interface = dict(interface)
    lowercase_category_interface["category"] = "productivity"
    lowercase_category_manifest["interface"] = lowercase_category_interface
    try:
        plugin_builder.validate_manifest(
            lowercase_category_manifest,
            source_state.plugin_version,
            GENERATED_PACKAGE_ROOT,
        )
    except plugin_builder.BuildError:
        pass
    else:
        fail("manifest interface.category must reject lowercase productivity")

    if path_exists(ROOT_PLUGIN_MANIFEST_FILE):
        fail("root .codex-plugin/plugin.json must not exist after Packaging Phase 2")

    validate_generated_git_state()

    marketplace = load_json_object(MARKETPLACE_FILE, "marketplace")
    if MARKETPLACE_FILE.is_symlink() or not MARKETPLACE_FILE.is_file():
        fail("marketplace must be a regular file, not a symlink")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        fail("marketplace plugins must be an array")
    matches = [
        item for item in plugins
        if isinstance(item, dict) and item.get("name") == SKILL_NAME
    ]
    if len(matches) != 1:
        fail(f"marketplace must contain exactly one {SKILL_NAME} plugin")
    source = matches[0].get("source")
    if not isinstance(source, dict):
        fail("marketplace target plugin source must be an object")
    marketplace_target = validate_marketplace_path(source.get("path"))

    package_valid = False
    if path_exists(marketplace_target):
        try:
            plugin_builder.check_package()
        except plugin_builder.BuildError as exc:
            fail(f"local generated package is invalid: {exc}")
        package_valid = True

    submission = load_json_object(SUBMISSION_TESTS_FILE, "submission tests")
    if submission.get("plugin") != SKILL_NAME:
        fail("submission tests plugin name does not match")
    if submission.get("plugin_version") != plugin_version:
        fail("submission tests plugin_version must match PLUGIN_VERSION")
    if submission.get("core_skill_version") != version:
        fail("submission tests core_skill_version must match VERSION")

    submission_cases = submission.get("cases")
    if not isinstance(submission_cases, list):
        fail("submission tests cases must be an array")

    positive_count = 0
    negative_count = 0
    seen_submission_ids: set[str] = set()
    for index, case in enumerate(submission_cases):
        label = f"submission test at index {index}"
        if not isinstance(case, dict):
            fail(f"{label} must be an object")
        case_id = case.get("id")
        diagnostic_id = case_id if isinstance(case_id, str) and case_id.strip() else f"at index {index}"
        case_id = require_non_empty_string(case, "id", diagnostic_id)
        if case_id in seen_submission_ids:
            fail(f"duplicate submission test id: {case_id}")
        seen_submission_ids.add(case_id)

        for field in COMMON_SUBMISSION_STRING_FIELDS:
            require_non_empty_string(case, field, case_id)

        case_type = case["type"]
        if case_type == "positive":
            for field in POSITIVE_STRING_ARRAY_FIELDS:
                require_non_empty_string_array(case, field, case_id)
            positive_count += 1
        elif case_type == "negative":
            for field in NEGATIVE_STRING_FIELDS:
                require_non_empty_string(case, field, case_id)
            negative_count += 1
        else:
            fail(
                f"submission test {case_id} field type must be 'positive' or 'negative'; "
                f"actual value: {case_type!r}"
            )

    if positive_count < 5:
        fail("submission tests must contain at least 5 positive cases")
    if negative_count < 3:
        fail("submission tests must contain at least 3 negative cases")

    skill_files = repository_skill_files()
    expected_skill_files = ["skills/first-principles-thinking/SKILL.md"]
    if skill_files != expected_skill_files:
        fail(
            "repository must contain only the canonical core SKILL.md; "
            f"found: {', '.join(skill_files)}"
        )

    for document in ROOT.rglob("*.md"):
        if ".git" in document.parts or ".build" in document.parts:
            continue
        text = document.read_text(encoding="utf-8")
        match = PLACEHOLDER_RE.search(text)
        if match:
            fail(
                f"documentation contains placeholder {match.group(0)}: "
                f"{document.relative_to(ROOT)}"
            )
    manifest_text = PLUGIN_MANIFEST_FILE.read_text(encoding="utf-8")
    match = PLACEHOLDER_RE.search(manifest_text)
    if match:
        fail(f"plugin manifest contains placeholder {match.group(0)}")

    return (
        plugin_version,
        positive_count,
        negative_count,
        package_valid,
    )


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

    (
        plugin_version,
        positive_count,
        negative_count,
        package_valid,
    ) = validate_plugin(version)
    skill_sha256 = hashlib.sha256(SKILL_FILE.read_bytes()).hexdigest()

    print(f"PASS: {SKILL_NAME} v{version}")
    print(f"PASS: Core Skill version {version}")
    print(f"PASS: Plugin version {plugin_version}")
    print("PASS: README.md current version matches VERSION")
    print(f"PASS: CHANGELOG.md contains [{version}]")
    print("PASS: evals/README.md exists")
    print(f"PASS: {len(cases)} eval cases")
    print(f"PASS: SKILL.md has {line_count} lines")
    print(f"PASS: {positive_count} positive and {negative_count} negative submission tests")
    print("PASS: canonical plugin manifest and repo-local marketplace validated")
    print("PASS: lowercase category productivity is rejected")
    print("PASS: root compatibility manifest is absent")
    print("PASS: .build is ignored and contains no tracked files")
    print("PASS: canonical SKILL.md is the only SKILL.md in the repository")
    print(f"PASS: Core Skill SHA-256 {skill_sha256}")
    print("Repository valid: PASS")
    if package_valid:
        print("Local package valid: PASS")
    else:
        print("Local package valid: NOT BUILT (run tools/build_openai_plugin.py)")
    print("Directory submission readiness: NOT ASSESSED")
    print(
        "Directory assets and Portal metadata are deferred to the Portal submission stage."
    )
    print("PASS: repository validation completed")


if __name__ == "__main__":
    main()
