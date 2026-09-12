#!/usr/bin/env python3
"""Promotes CHANGELOG.md's Unreleased section to a new version heading.

Run by scripts/git-hooks/pre-commit as part of every code-touching commit
to the target branch (SDSI.md §17) — not meant to be run by hand in
normal use. Renames the "## 🚧 Unreleased" heading to "## 🆕VERSION
<version> 📅 <date>" (its own bullets, whatever was filled in during the
session, move with it unchanged), rolls whichever entry currently holds
🆕 to the next color in the rotation, and inserts a fresh, empty
Unreleased section back at the very top.

Refuses (exit 1, writes nothing) if Unreleased has no real content yet —
every one of its four subsections still reading "(none)". An empty entry
silently promoted into a version heading defeats the whole point of this
policy: reading CHANGELOG.md for a version has to actually show what
changed. Add a bullet under whichever subsection it belongs to, then
commit.

Idempotent: if "## 🚧 Unreleased" isn't present at all (already promoted
by hand earlier in the same commit), this is a no-op — an already-edited
changelog is left alone rather than double-promoted.
"""
import re
import sys
from datetime import date
from pathlib import Path

CHANGELOG_PATH = Path(__file__).resolve().parents[2] / "CHANGELOG.md"

# The fixed rotation every already-shipped entry's marker cycles through
# (SDSI.md §17), wrapping back to the first after the last.
COLORS = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫"]

UNRELEASED_HEADING = "## 🚧 Unreleased"
EMPTY_UNRELEASED = """## 🚧 Unreleased

### Added or New Features
(none)

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)
"""


def unreleased_body(text):
    """The text between the Unreleased heading and the next '## ' heading.

    Input:
        text (str): the changelog's current contents.
    Output:
        str | None: the body text, or None if Unreleased isn't present.
    """
    match = re.search(
        r"^## 🚧 Unreleased\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
    )
    return match.group(1) if match else None


def unreleased_is_empty(text):
    """True if Unreleased has no bullet under any of its four subsections.

    Input:
        text (str): the changelog's current contents.
    Output:
        bool: True if Unreleased is absent, or present but contentless.
    """
    body = unreleased_body(text)
    if body is None:
        return False  # absent means already promoted, not empty — see main()
    return re.search(r"^- ", body, re.MULTILINE) is None


def next_color(text):
    """The color that follows whichever entry currently holds 🆕.

    Input:
        text (str): the changelog's current contents.
    Output:
        str: the next color in COLORS' rotation, or COLORS[0] when there is
        no 🆕 entry yet (the very first promotion).
    """
    match = re.search(r"^## 🆕VERSION", text, re.MULTILINE)
    if match is None:
        return COLORS[0]
    colored_count = len(
        re.findall(r"^## (?:🟥|🟧|🟨|🟩|🟦|🟪|🟫)VERSION", text, re.MULTILINE)
    )
    return COLORS[colored_count % len(COLORS)]


def promote(text, version):
    """Rename Unreleased to the new version heading and roll the old 🆕.

    Input:
        text (str): the changelog's current contents.
        version (str): the version this heading gets, e.g. "0.1.4".
    Output:
        str: the updated contents, or the input unchanged if Unreleased
        was already promoted (idempotent).
    """
    if UNRELEASED_HEADING not in text:
        return text

    color = next_color(text)
    text = re.sub(
        r"^## 🆕VERSION", f"## {color}VERSION", text, count=1, flags=re.MULTILINE
    )

    today = date.today().isoformat()
    promoted_heading = f"## 🆕VERSION {version} 📅 {today}"
    return text.replace(UNRELEASED_HEADING, f"{EMPTY_UNRELEASED}\n{promoted_heading}", 1)


def main():
    """Entry point: promote CHANGELOG.md for the version named on argv[1].

    Input:
        sys.argv[1] (str): the version, e.g. "0.1.4".
    Output:
        int: process exit code. 0 on a successful promotion or an
        already-promoted no-op; 1 (refusing the commit) if Unreleased has
        no content yet to promote.
    """
    version = sys.argv[1]
    text = CHANGELOG_PATH.read_text(encoding="utf-8")

    if unreleased_is_empty(text):
        print(
            "bump_changelog: '## 🚧 Unreleased' has no entries yet — "
            "add a bullet under Added/Removed/Changed/Bug fixes describing "
            "this change before committing (or commit --no-verify if this "
            "genuinely isn't a release).",
            file=sys.stderr,
        )
        return 1

    updated = promote(text, version)
    if updated != text:
        CHANGELOG_PATH.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
