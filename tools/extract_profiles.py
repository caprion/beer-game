from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document


def extract(docx_path: Path) -> str:
    doc = Document(str(docx_path))
    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            lines.append("")
            continue
        style = getattr(para.style, "name", "") or ""
        if style.startswith("Heading"):
            level = style.replace("Heading ", "")
            try:
                level_i = max(2, min(4, int(level)))
            except Exception:
                level_i = 3
            lines.append("#" * level_i + " " + text)
        else:
            lines.append(text)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--out", type=Path, default=Path("docs/PROFILES.md"))
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    content = extract(args.docx)
    args.out.write_text(content, encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()


