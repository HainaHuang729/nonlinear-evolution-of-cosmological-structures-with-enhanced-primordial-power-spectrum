#!/usr/bin/env python3
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "overleaf_review_body_text.txt"
JSON_OUT = ROOT / "overleaf_review_comments_parsed.json"
MD_OUT = ROOT / "overleaf_review_comments_parsed.md"

AUTHOR = "tkc004"
TIME_RE = re.compile(r"^(?:\d{1,2} May|1 June), \d{1,2}:\d{2} (?:am|pm)$")
UI_TOKENS = {
    "check",
    "Resolve comment",
    "more_vert",
    "More options",
    "Reply",
    "show less",
    "show more",
}
TRAILING_STOP = {"description", "Current file", "list", "Overview", "chevron_left", "Recompile"}


def is_comment_start(lines, index):
    return index + 1 < len(lines) and lines[index] == AUTHOR and TIME_RE.match(lines[index + 1])


def parse_comments(lines):
    comments = []
    index = 0
    while index < len(lines):
        if not is_comment_start(lines, index):
            index += 1
            continue

        source_line = index + 1
        author = lines[index]
        timestamp = lines[index + 1]
        index += 2

        text_parts = []
        while index < len(lines):
            line = lines[index]
            if is_comment_start(lines, index):
                break
            if line in TRAILING_STOP:
                break
            if line and line not in UI_TOKENS:
                text_parts.append(line)
            index += 1

        text = " ".join(text_parts).strip()
        text = re.sub(r"\s+", " ", text)
        if text:
            comments.append(
                {
                    "index": len(comments) + 1,
                    "source_line": source_line,
                    "author": author,
                    "timestamp": timestamp,
                    "text": text,
                }
            )

    return comments


def write_markdown(comments):
    lines = [
        "# Overleaf Review Comments Export",
        "",
        f"Source: `{SOURCE}`",
        "",
        f"Total parsed comments/messages: {len(comments)}",
        "",
    ]
    for item in comments:
        lines.extend(
            [
                f"## {item['index']}. {item['author']} - {item['timestamp']}",
                "",
                item["text"],
                "",
            ]
        )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    raw_lines = SOURCE.read_text(encoding="utf-8", errors="replace").splitlines()
    lines = [line.strip() for line in raw_lines]
    comments = parse_comments(lines)
    JSON_OUT.write_text(
        json.dumps({"source": str(SOURCE), "count": len(comments), "comments": comments}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(comments)
    print(f"parsed {len(comments)} comments/messages")
    print(JSON_OUT)
    print(MD_OUT)


if __name__ == "__main__":
    main()
