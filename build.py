#!/usr/bin/env python3
"""Build fortune data files from the YAML source."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parent
SOURCE = PROJECT / "gushici.yaml"
CHT_OUTPUT = PROJECT / "data" / "gushici-cht"
FortuneUnit = dict[str, Any] | list[dict[str, Any]]

ANSI_RE = re.compile(r"\033\[[0-9;]*m")
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_ITALIC = "\033[3m"


def load_poems() -> list[dict[str, Any]]:
    poems = load_source_data()
    if not isinstance(poems, list):
        raise ValueError(f"{SOURCE.name} must contain a top-level list")
    if not all(isinstance(poem, dict) for poem in poems):
        raise ValueError(f"{SOURCE.name} must contain only mapping items")
    return poems


def load_source_data() -> list[dict[str, Any]]:
    if not SOURCE.exists():
        raise FileNotFoundError(f"missing source file: {SOURCE.name}")
    return load_yaml_source(SOURCE)


def load_yaml_source(path: Path) -> list[dict[str, Any]]:
    if shutil.which("ruby"):
        return load_yaml_with_ruby(path)
    return load_yaml_with_pyyaml(path)


def load_yaml_with_ruby(path: Path) -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            [
                "ruby",
                "-rjson",
                "-ryaml",
                "-e",
                "data = YAML.safe_load(File.read(ARGV[0]), permitted_classes: [], aliases: false); print JSON.generate(data)",
                str(path),
            ],
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        raise RuntimeError(f"failed to load YAML source {path.name}: {detail}") from exc

    data = json.loads(result.stdout)
    if not isinstance(data, list):
        raise ValueError(f"{path.name} must decode to a list")
    return data


def load_yaml_with_pyyaml(path: Path) -> list[dict[str, Any]]:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "YAML parser unavailable: install Ruby or run 'python3 -m pip install pyyaml'"
        ) from exc

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path.name} must decode to a list")
    return data


def validate_credit_part(index: int, poem: dict[str, Any], label: str, errors: list[str]) -> None:
    dynasty = poem.get("dynasty")
    authors = poem.get("authors")
    title = poem.get("title")
    suffix = poem.get("suffix")

    if not isinstance(dynasty, str) or not dynasty.strip():
        errors.append(f"poem #{index} {label}: dynasty must be a non-empty string")
    if not isinstance(authors, list) or not authors:
        errors.append(f"poem #{index} {label}: authors must be a non-empty array")
    elif not all(isinstance(author, str) and author.strip() for author in authors):
        errors.append(f"poem #{index} {label}: authors contains an empty/non-string item")
    if not isinstance(title, list) or not title:
        errors.append(f"poem #{index} {label}: title must be a non-empty array")
    elif not all(isinstance(part, str) and part.strip() for part in title):
        errors.append(f"poem #{index} {label}: title contains an empty/non-string item")
    if suffix is not None and (not isinstance(suffix, str) or not suffix.strip()):
        errors.append(f"poem #{index} {label}: suffix must be a non-empty string when present")


def validate_poems(poems: list[dict[str, Any]]) -> None:
    errors: list[str] = []
    for index, poem in enumerate(poems, 1):
        body = poem.get("body")
        notes = poem.get("notes", [])
        group = poem.get("group")
        alias = poem.get("alias")

        if not isinstance(body, str) or not body.strip():
            errors.append(f"poem #{index}: body must be a non-empty string")
        if group is not None:
            if not isinstance(group, str) or not group.strip():
                errors.append(f"poem #{index}: group must be a non-empty string when present")
            elif ANSI_RE.search(group):
                errors.append(f"poem #{index}: group must not contain ANSI escapes")
        if alias is not None:
            aliases = [alias] if isinstance(alias, str) else alias
            if not isinstance(aliases, list):
                errors.append(f"poem #{index}: alias must be a string or array when present")
                aliases = []
            for item in aliases:
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"poem #{index}: alias contains an empty/non-string item")
                elif ANSI_RE.search(item):
                    errors.append(f"poem #{index}: alias must not contain ANSI escapes")
        if not isinstance(notes, list):
            errors.append(f"poem #{index}: notes must be an array when present")
            notes = []

        validate_credit_part(index, poem, "main", errors)

        for note in notes:
            if not isinstance(note, str) or not note.strip():
                errors.append(f"poem #{index}: notes contains an empty/non-string item")
            elif ANSI_RE.search(note):
                errors.append(f"poem #{index}: notes must not contain ANSI escapes")

        if isinstance(body, str):
            if ANSI_RE.search(body):
                errors.append(f"poem #{index}: body must not contain ANSI escapes")
            if any(line == "%" for line in body.splitlines()):
                errors.append(f"poem #{index}: body must not contain a standalone % line")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)


def title_text(poem: dict[str, Any]) -> str:
    return "·".join(poem["title"])


def alias_texts(poem: dict[str, Any]) -> list[str]:
    alias = poem.get("alias")
    if alias is None:
        return []
    aliases = [alias] if isinstance(alias, str) else alias
    if not isinstance(aliases, list):
        return []
    return [item.strip() for item in aliases if isinstance(item, str) and item.strip()]


def poem_group(poem: dict[str, Any]) -> str | None:
    group = poem.get("group")
    if isinstance(group, str) and group.strip():
        return group.strip()
    return None


def display_credit(poem: dict[str, Any]) -> str:
    title = f"《{title_text(poem)}》{poem.get('suffix', '')}"
    authors = "/".join(poem["authors"])
    dynasty = poem["dynasty"]
    if dynasty == "_":
        return f"{authors}{title}"
    return f"{dynasty}·{authors}{title}"


def format_bold(text: str) -> str:
    return f"{ANSI_BOLD}{text}{ANSI_RESET}"


def format_italic(text: str) -> str:
    return f"{ANSI_ITALIC}{text}{ANSI_RESET}"


def display_author(poem: dict[str, Any]) -> str:
    authors = "/".join(poem["authors"])
    dynasty = poem["dynasty"]
    if dynasty == "_":
        return authors
    return f"{dynasty}·{authors}"


def unique_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def group_authors(poems: list[dict[str, Any]]) -> list[str]:
    return unique_values([author for poem in poems for author in poem["authors"]])


def group_dynasties(poems: list[dict[str, Any]]) -> list[str]:
    return unique_values([poem["dynasty"] for poem in poems if poem["dynasty"] != "_"])


def display_group_credit(poems: list[dict[str, Any]]) -> str:
    first_title = poems[0]["title"]
    if not all(poem["title"] == first_title for poem in poems):
        return " / ".join(display_credit(poem) for poem in poems)
    title = f"《{title_text(poems[0])}》"
    authors = "/".join(group_authors(poems))
    dynasties = group_dynasties(poems)
    if not dynasties:
        return f"{authors}{title}"
    return f"{'/'.join(dynasties)}·{authors}{title}"


def iter_fortune_units(poems: list[dict[str, Any]]) -> list[FortuneUnit]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for poem in poems:
        key = poem_group(poem)
        if key is not None:
            groups.setdefault(key, []).append(poem)

    units: list[FortuneUnit] = []
    emitted_groups: set[str] = set()
    for poem in poems:
        key = poem_group(poem)
        if key is None:
            units.append(poem)
            continue
        if key in emitted_groups:
            continue
        emitted_groups.add(key)
        grouped = groups[key]
        units.append(grouped if len(grouped) > 1 else poem)
    return units


def render_poem_header(poem: dict[str, Any], use_ansi: bool = False) -> list[str]:
    title = f"{title_text(poem)}{poem.get('suffix', '')}"
    if use_ansi:
        title = format_bold(title)
    lines = [title]
    aliases = alias_texts(poem)
    if aliases:
        lines.append(f"又名：{'、'.join(aliases)}")
    lines.append(display_author(poem))
    annotations = poem.get("notes", [])
    if annotations:
        lines.append("")
        if use_ansi:
            lines.extend(format_italic(note) for note in annotations)
        else:
            lines.extend(annotations)
    return lines


def render_poem(poem: dict[str, Any], use_ansi: bool = False) -> str:
    lines = render_poem_header(poem, use_ansi=use_ansi)
    lines.extend(["", poem["body"].strip("\n")])
    return "\n".join(lines)


def render_group_member(poem: dict[str, Any], use_ansi: bool = False) -> str:
    return render_poem(poem, use_ansi=use_ansi)


def render_group(poems: list[dict[str, Any]], use_ansi: bool = False) -> str:
    return "\n\n".join(render_group_member(poem, use_ansi=use_ansi) for poem in poems)


def display_unit_credit(unit: FortuneUnit) -> str:
    if isinstance(unit, list):
        return display_group_credit(unit)
    return display_credit(unit)


def render_unit(unit: FortuneUnit, use_ansi: bool = False) -> str:
    if isinstance(unit, list):
        return render_group(unit, use_ansi=use_ansi)
    return render_poem(unit, use_ansi=use_ansi)


def render_fortune(units: list[FortuneUnit], use_ansi: bool = False) -> str:
    return "\n%\n".join(render_unit(unit, use_ansi=use_ansi) for unit in units) + "\n"


def write_output(units: list[FortuneUnit], use_ansi: bool = False) -> None:
    CHT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    CHT_OUTPUT.write_text(render_fortune(units, use_ansi=use_ansi), encoding="utf-8")


def opencc_convert(text: str, config: str) -> str | None:
    if not shutil.which("opencc"):
        return None
    try:
        result = subprocess.run(
            ["opencc", "-c", config],
            input=text,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout


def search_terms(keyword: str) -> set[str]:
    terms = {keyword.casefold()}
    for config in ("s2t.json", "t2s.json"):
        converted = opencc_convert(keyword, config)
        if converted:
            terms.add(converted.casefold())
    return terms


def searchable_text(poem: dict[str, Any]) -> str:
    fields = [poem["body"], title_text(poem), display_credit(poem), *alias_texts(poem), *poem.get("notes", [])]
    group = poem_group(poem)
    if group is not None:
        fields.append(group)
    return "\n".join(fields)


def searchable_unit_text(unit: FortuneUnit) -> str:
    if isinstance(unit, list):
        fields = [display_group_credit(unit)]
        fields.extend(searchable_text(poem) for poem in unit)
        return "\n".join(fields)
    return searchable_text(unit)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="list final poem credits from the YAML source")
    parser.add_argument("--check", metavar="KEYWORD", help="search final poem credits from the YAML source")
    parser.add_argument("--ansi", action="store_true", help="render ANSI formatting in generated fortune text")
    args = parser.parse_args(argv)

    poems = load_poems()
    validate_poems(poems)
    units = iter_fortune_units(poems)

    if args.list:
        for unit in units:
            print(display_unit_credit(unit))
        return 0

    if args.check is not None:
        terms = search_terms(args.check)
        matches = []
        for unit in units:
            searchable = searchable_unit_text(unit).casefold()
            if any(term in searchable for term in terms):
                matches.append(display_unit_credit(unit))
        if matches:
            print("\n".join(matches))
        else:
            print("未找到匹配條目")
        return 0

    write_output(units, use_ansi=args.ansi)
    source = os.path.relpath(SOURCE, PROJECT)
    output = os.path.relpath(CHT_OUTPUT, PROJECT)
    print(f"Generated {output} from {source} ({len(units)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
