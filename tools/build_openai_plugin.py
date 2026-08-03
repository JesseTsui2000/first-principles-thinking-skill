#!/usr/bin/env python3
"""Build and verify the generated OpenAI skills-only Plugin package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "first-principles-thinking"
EXPECTED_SKILL_SHA256 = (
    "2aa3d0c8ac0093ac5e40e281c8eb3807541733b56c0d394c3a3d017ef9f3c395"
)
STRICT_THREE_PART_VERSION_RE = re.compile(r"\d+\.\d+\.\d+")
ALLOWED_PLUGIN_CATEGORIES = {"productivity"}

SKILL_FILE = ROOT / "skills" / SKILL_NAME / "SKILL.md"
MANIFEST_FILE = ROOT / "packaging" / "openai-plugin" / "plugin.json"
VERSION_FILE = ROOT / "VERSION"
PLUGIN_VERSION_FILE = ROOT / "PLUGIN_VERSION"
SUBMISSION_TESTS_FILE = ROOT / "plugin-submission" / "test-cases.json"

OUTPUT_PARENT = ROOT / ".build" / "plugins"
OUTPUT_ROOT = OUTPUT_PARENT / SKILL_NAME
PACKAGE_SKILL = Path("skills") / SKILL_NAME / "SKILL.md"
PACKAGE_MANIFEST = Path(".codex-plugin") / "plugin.json"
PACKAGE_FILES = (PACKAGE_MANIFEST, PACKAGE_SKILL)
PACKAGE_DIRECTORIES = {
    Path(".codex-plugin"),
    Path("skills"),
    Path("skills") / SKILL_NAME,
}

PROHIBITED_CONFIG_KEYS = {
    "app",
    "apps",
    "hook",
    "hooks",
    "mcp",
    "mcpserver",
    "mcpservers",
    "screenshot",
    "screenshots",
}
PORTAL_READY_KEYS = {"portalready", "portalreadiness", "portalstatus"}
PORTAL_REQUIRED_FIELDS = (
    "author.name",
    "interface.developerName",
    "publisherUrl",
    "supportUrl",
    "privacyUrl",
    "termsUrl",
    "logo",
)


class BuildError(RuntimeError):
    """Raised when a source or generated package violates the build contract."""


@dataclass(frozen=True)
class SourceState:
    core_version: str
    plugin_version: str
    skill_bytes: bytes
    manifest_bytes: bytes
    skill_sha256: str
    manifest_sha256: str
    manifest: dict[str, object]
    portal_missing_fields: tuple[str, ...]


@dataclass(frozen=True)
class PackageState:
    skill_sha256: str
    manifest_sha256: str
    files: tuple[str, ...]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def normalized_key(key: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def path_exists(path: Path) -> bool:
    return os.path.lexists(path)


def is_strict_three_part_version(value: str) -> bool:
    return STRICT_THREE_PART_VERSION_RE.fullmatch(value) is not None


def require_fixed_regular_file(path: Path, label: str) -> bytes:
    if not path.is_absolute():
        raise BuildError(f"{label} path is not absolute: {path}")
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise BuildError(f"{label} must remain inside the repository root") from exc
    if not path_exists(path):
        raise BuildError(f"{label} is missing: {path.relative_to(ROOT)}")
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode):
        raise BuildError(f"{label} must not be a symlink: {path.relative_to(ROOT)}")
    if not stat.S_ISREG(mode):
        raise BuildError(f"{label} must be a regular file: {path.relative_to(ROOT)}")
    if path.resolve(strict=True) != path:
        raise BuildError(f"{label} has a symlink in its resolved path")
    return path.read_bytes()


def require_json_object(content: bytes, label: str) -> dict[str, object]:
    try:
        parsed = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise BuildError(f"{label} must contain a JSON object")
    return parsed


def find_nested_key(data: object, prohibited: set[str]) -> str | None:
    if isinstance(data, dict):
        for key, value in data.items():
            if normalized_key(key) in prohibited:
                return str(key)
            nested = find_nested_key(value, prohibited)
            if nested is not None:
                return nested
    elif isinstance(data, list):
        for value in data:
            nested = find_nested_key(value, prohibited)
            if nested is not None:
                return nested
    return None


def nested_value(data: dict[str, object], dotted_path: str) -> object | None:
    value: object = data
    for component in dotted_path.split("."):
        if not isinstance(value, dict) or component not in value:
            return None
        value = value[component]
    return value


def validate_manifest(
    manifest: dict[str, object], plugin_version: str, package_root: Path
) -> tuple[str, ...]:
    if manifest.get("name") != SKILL_NAME:
        raise BuildError(f"manifest name must be {SKILL_NAME}")
    if manifest.get("version") != plugin_version:
        raise BuildError("manifest version must match PLUGIN_VERSION")

    author = manifest.get("author")
    if not isinstance(author, dict):
        raise BuildError("manifest author must be an object")
    author_name = author.get("name")
    if not isinstance(author_name, str) or not author_name.strip():
        raise BuildError("manifest author.name must be a non-empty string")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        raise BuildError("manifest interface must be an object")
    developer_name = interface.get("developerName")
    if not isinstance(developer_name, str) or not developer_name.strip():
        raise BuildError("manifest interface.developerName must be a non-empty string")
    category = interface.get("category")
    if category not in ALLOWED_PLUGIN_CATEGORIES:
        allowed = ", ".join(sorted(ALLOWED_PLUGIN_CATEGORIES))
        raise BuildError(f"manifest interface.category must be one of: {allowed}")
    capabilities = interface.get("capabilities")
    if (
        not isinstance(capabilities, list)
        or not capabilities
        or not all(isinstance(value, str) and value.strip() for value in capabilities)
    ):
        raise BuildError(
            "manifest interface.capabilities must be a non-empty array of non-empty strings"
        )

    skills_path = manifest.get("skills")
    if skills_path != "./skills/":
        raise BuildError("manifest skills must be exactly ./skills/")
    pure_skills_path = PurePosixPath(skills_path)
    if pure_skills_path.is_absolute() or ".." in pure_skills_path.parts:
        raise BuildError("manifest skills must remain inside the Plugin root")
    resolved_skills = (package_root / skills_path).resolve(strict=False)
    resolved_root = package_root.resolve(strict=False)
    try:
        resolved_skills.relative_to(resolved_root)
    except ValueError as exc:
        raise BuildError("manifest skills resolves outside the Plugin root") from exc
    if resolved_skills != resolved_root / "skills":
        raise BuildError("manifest skills must resolve to the package skills directory")

    prohibited = find_nested_key(manifest, PROHIBITED_CONFIG_KEYS)
    if prohibited is not None:
        raise BuildError(f"manifest contains prohibited MCP/App/screenshot key: {prohibited}")

    for key, value in manifest.items():
        if normalized_key(key) in PORTAL_READY_KEYS and value not in (False, None, "NOT READY"):
            raise BuildError("manifest must not mark the current package as Portal-ready")

    return tuple(
        field
        for field in PORTAL_REQUIRED_FIELDS
        if not isinstance(nested_value(manifest, field), str)
        or not str(nested_value(manifest, field)).strip()
    )


def parse_skill_version(skill_bytes: bytes) -> str:
    try:
        text = skill_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BuildError(f"canonical SKILL.md must be UTF-8: {exc}") from exc
    if not text.startswith("---\n"):
        raise BuildError("canonical SKILL.md must begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise BuildError("canonical SKILL.md frontmatter is not closed")
    match = re.search(r"^  version:\s*['\"]?([^'\"\s]+)['\"]?\s*$", text[4:end], re.MULTILINE)
    if match is None:
        raise BuildError("canonical SKILL.md metadata.version is missing")
    return match.group(1)


def validate_sources() -> SourceState:
    skill_bytes = require_fixed_regular_file(SKILL_FILE, "canonical Skill")
    manifest_bytes = require_fixed_regular_file(MANIFEST_FILE, "canonical manifest")
    version_bytes = require_fixed_regular_file(VERSION_FILE, "VERSION")
    plugin_version_bytes = require_fixed_regular_file(PLUGIN_VERSION_FILE, "PLUGIN_VERSION")
    submission_bytes = require_fixed_regular_file(SUBMISSION_TESTS_FILE, "submission tests")

    try:
        core_version = version_bytes.decode("utf-8").strip()
        plugin_version = plugin_version_bytes.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise BuildError(f"version files must be UTF-8: {exc}") from exc
    if not is_strict_three_part_version(core_version):
        raise BuildError("VERSION must use MAJOR.MINOR.PATCH")
    if not is_strict_three_part_version(plugin_version):
        raise BuildError("PLUGIN_VERSION must use MAJOR.MINOR.PATCH")

    skill_version = parse_skill_version(skill_bytes)
    if skill_version != core_version:
        raise BuildError("VERSION must match SKILL.md metadata.version")

    skill_sha256 = sha256_bytes(skill_bytes)
    if skill_sha256 != EXPECTED_SKILL_SHA256:
        raise BuildError(
            "canonical Skill SHA-256 does not match the protected Packaging Phase 2 value"
        )

    manifest = require_json_object(manifest_bytes, "canonical manifest")
    portal_missing_fields = validate_manifest(manifest, plugin_version, OUTPUT_ROOT)

    eval_bytes = require_fixed_regular_file(
        ROOT / "skills" / SKILL_NAME / "evals" / "evals.json", "Core evals"
    )
    eval_data = require_json_object(eval_bytes, "Core evals")
    if eval_data.get("version") != core_version:
        raise BuildError("VERSION must match evals.json version")

    submission = require_json_object(submission_bytes, "submission tests")
    if submission.get("core_skill_version") != core_version:
        raise BuildError("submission tests core_skill_version must match VERSION")
    if submission.get("plugin_version") != plugin_version:
        raise BuildError("submission tests plugin_version must match PLUGIN_VERSION")

    return SourceState(
        core_version=core_version,
        plugin_version=plugin_version,
        skill_bytes=skill_bytes,
        manifest_bytes=manifest_bytes,
        skill_sha256=skill_sha256,
        manifest_sha256=sha256_bytes(manifest_bytes),
        manifest=manifest,
        portal_missing_fields=portal_missing_fields,
    )


def require_no_symlink_components(path: Path, base: Path = ROOT) -> None:
    try:
        relative = path.relative_to(base)
    except ValueError as exc:
        raise BuildError(f"output path escapes repository root: {path}") from exc
    current = base
    for component in relative.parts:
        current = current / component
        if not path_exists(current):
            continue
        mode = current.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise BuildError(f"output path must not contain symlinks: {current}")


def validate_output_location() -> None:
    expected = ROOT / ".build" / "plugins" / SKILL_NAME
    if OUTPUT_ROOT != expected:
        raise BuildError("internal output path does not match the fixed package location")
    require_no_symlink_components(OUTPUT_ROOT)
    if OUTPUT_ROOT.resolve(strict=False) != expected:
        raise BuildError("resolved output path does not match the fixed package location")
    for directory in (ROOT / ".build", OUTPUT_PARENT, OUTPUT_ROOT):
        if path_exists(directory) and not stat.S_ISDIR(directory.lstat().st_mode):
            raise BuildError(f"output path component must be a directory: {directory}")


def scan_package(package_root: Path) -> tuple[set[Path], set[Path]]:
    if not path_exists(package_root):
        raise BuildError(f"generated package is missing: {package_root}")
    root_mode = package_root.lstat().st_mode
    if stat.S_ISLNK(root_mode) or not stat.S_ISDIR(root_mode):
        raise BuildError("generated package root must be a real directory")

    directories: set[Path] = set()
    files: set[Path] = set()

    def visit(directory: Path) -> None:
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda item: item.name):
                entry_path = Path(entry.path)
                relative = entry_path.relative_to(package_root)
                mode = entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):
                    raise BuildError(f"generated package contains a symlink: {relative}")
                if stat.S_ISDIR(mode):
                    directories.add(relative)
                    visit(entry_path)
                elif stat.S_ISREG(mode):
                    if entry.stat(follow_symlinks=False).st_nlink != 1:
                        raise BuildError(f"generated package contains a hardlink: {relative}")
                    files.add(relative)
                else:
                    raise BuildError(f"generated package contains a special file: {relative}")

    visit(package_root)
    return directories, files


def validate_package(
    package_root: Path, sources: SourceState, *, require_fixed_location: bool
) -> PackageState:
    if require_fixed_location:
        validate_output_location()
        if package_root != OUTPUT_ROOT:
            raise BuildError("package check only accepts the fixed generated package root")
    else:
        if package_root.parent != OUTPUT_PARENT or not package_root.name.startswith(
            f".{SKILL_NAME}.tmp-"
        ):
            raise BuildError("temporary package must be a safely created output sibling")
        require_no_symlink_components(package_root)

    directories, files = scan_package(package_root)
    expected_files = set(PACKAGE_FILES)
    if files != expected_files:
        found = ", ".join(sorted(path.as_posix() for path in files)) or "none"
        raise BuildError(f"generated package file allowlist mismatch; found: {found}")
    if directories != PACKAGE_DIRECTORIES:
        found = ", ".join(sorted(path.as_posix() for path in directories)) or "none"
        raise BuildError(f"generated package directory allowlist mismatch; found: {found}")
    if sum(1 for path in files if path.name == "SKILL.md") != 1:
        raise BuildError("generated package must contain exactly one SKILL.md")

    package_skill_path = package_root / PACKAGE_SKILL
    package_manifest_path = package_root / PACKAGE_MANIFEST
    package_skill_bytes = package_skill_path.read_bytes()
    package_manifest_bytes = package_manifest_path.read_bytes()
    if package_skill_bytes != sources.skill_bytes:
        raise BuildError("generated Skill is stale or differs from canonical Skill")
    if package_manifest_bytes != sources.manifest_bytes:
        raise BuildError("generated manifest is stale or differs from canonical manifest")
    if os.path.samefile(package_skill_path, SKILL_FILE):
        raise BuildError("generated Skill must be a copy, not a hardlink")
    if os.path.samefile(package_manifest_path, MANIFEST_FILE):
        raise BuildError("generated manifest must be a copy, not a hardlink")

    package_skill_sha256 = sha256_bytes(package_skill_bytes)
    package_manifest_sha256 = sha256_bytes(package_manifest_bytes)
    if package_skill_sha256 != sources.skill_sha256:
        raise BuildError("generated Skill SHA-256 does not match canonical Skill")
    if package_skill_sha256 != EXPECTED_SKILL_SHA256:
        raise BuildError("generated Skill SHA-256 does not match the protected value")
    if package_manifest_sha256 != sources.manifest_sha256:
        raise BuildError("generated manifest SHA-256 does not match canonical manifest")

    package_manifest = require_json_object(package_manifest_bytes, "generated manifest")
    package_missing_fields = validate_manifest(
        package_manifest, sources.plugin_version, package_root
    )
    if package_missing_fields != sources.portal_missing_fields:
        raise BuildError("generated manifest Portal-readiness state differs from canonical source")

    return PackageState(
        skill_sha256=package_skill_sha256,
        manifest_sha256=package_manifest_sha256,
        files=tuple(sorted(path.as_posix() for path in files)),
    )


def create_output_parents() -> None:
    validate_output_location()
    for directory in (ROOT / ".build", OUTPUT_PARENT):
        if not path_exists(directory):
            directory.mkdir()
        mode = directory.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise BuildError(f"output parent must be a real directory: {directory}")
    validate_output_location()


def safe_remove_generated_tree(path: Path, allowed_names: set[str]) -> None:
    if path.parent != OUTPUT_PARENT or path.name not in allowed_names:
        raise BuildError(f"refusing to remove unexpected path: {path}")
    if not path_exists(path):
        return
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise BuildError(f"refusing to remove non-directory generated path: {path}")
    shutil.rmtree(path)


def print_summary(sources: SourceState, package: PackageState) -> None:
    print(f"Core Skill version: {sources.core_version}")
    print(f"Plugin wrapper version: {sources.plugin_version}")
    print(f"Canonical Skill SHA-256: {sources.skill_sha256}")
    print(f"Package Skill SHA-256: {package.skill_sha256}")
    print(f"Canonical manifest SHA-256: {sources.manifest_sha256}")
    print(f"Package manifest SHA-256: {package.manifest_sha256}")
    print(f"Package root: {OUTPUT_ROOT}")
    print(f"Package file allowlist: {', '.join(package.files)}")
    print("Portal-ready manifest: NOT READY (informational)")


def build_package() -> tuple[SourceState, PackageState]:
    sources = validate_sources()
    create_output_parents()
    temporary_root = Path(
        tempfile.mkdtemp(prefix=f".{SKILL_NAME}.tmp-", dir=OUTPUT_PARENT)
    )
    backup_root = OUTPUT_PARENT / f".{SKILL_NAME}.previous"
    replaced_existing = False

    try:
        (temporary_root / PACKAGE_MANIFEST.parent).mkdir(parents=True)
        (temporary_root / PACKAGE_SKILL.parent).mkdir(parents=True)
        shutil.copyfile(MANIFEST_FILE, temporary_root / PACKAGE_MANIFEST)
        shutil.copyfile(SKILL_FILE, temporary_root / PACKAGE_SKILL)
        validate_package(temporary_root, sources, require_fixed_location=False)

        if path_exists(backup_root):
            raise BuildError(f"refusing to overwrite stale backup directory: {backup_root}")
        if path_exists(OUTPUT_ROOT):
            validate_output_location()
            os.replace(OUTPUT_ROOT, backup_root)
            replaced_existing = True

        try:
            os.replace(temporary_root, OUTPUT_ROOT)
        except Exception:
            if replaced_existing and path_exists(backup_root) and not path_exists(OUTPUT_ROOT):
                os.replace(backup_root, OUTPUT_ROOT)
            raise

        try:
            package = validate_package(OUTPUT_ROOT, sources, require_fixed_location=True)
        except Exception:
            failed_root = temporary_root
            if path_exists(OUTPUT_ROOT):
                os.replace(OUTPUT_ROOT, failed_root)
            if replaced_existing and path_exists(backup_root):
                os.replace(backup_root, OUTPUT_ROOT)
            raise

        if path_exists(backup_root):
            safe_remove_generated_tree(backup_root, {backup_root.name})
        return sources, package
    finally:
        if path_exists(temporary_root):
            safe_remove_generated_tree(
                temporary_root,
                {temporary_root.name},
            )


def check_package() -> tuple[SourceState, PackageState]:
    sources = validate_sources()
    validate_output_location()
    package = validate_package(OUTPUT_ROOT, sources, require_fixed_location=True)
    return sources, package


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build or check the fixed OpenAI Plugin package."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="read-only verification of the existing generated package",
    )
    args = parser.parse_args()

    try:
        if args.check:
            sources, package = check_package()
            print_summary(sources, package)
            print("PACKAGE CHECK PASS")
        else:
            sources, package = build_package()
            print_summary(sources, package)
            print("BUILD PASS")
    except BuildError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
