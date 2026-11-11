# /// script
# requires-python = ">=3.12"
# dependencies = ["imgen", "pyyaml"]
# [tool.uv.sources]
# imgen = { path = "../../imgen", editable = true }
# ///
"""Generate mascot plates. Every roll is kept in art/rolls/<id>/<stamp>.png.

    uv run --env-file ../cecil/.env art/generate.py [id ...]   # REPLICATE_API_TOKEN

Pick a roll with art/pick.sh <id> <stamp>.
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
from imgen import generate_to  # ty: ignore[unresolved-import]  -- PEP 723 dep, not in the venv

STYLE = (
    "Natural history illustration from a 19th-century zoology book: {subject}. "
    "Fine black ink line drawing with pen hatching, hand-tinted with delicate, "
    "slightly uneven watercolour washes. Plain aged cream paper background, evenly "
    "lit, filling the whole square. One specimen, centred, the whole animal inside "
    "the frame with a generous margin. No text, no lettering, no labels, no figure "
    "numbers, no border, no frame, no caption."
)

SUBJECTS = yaml.safe_load((Path(__file__).parent / "subjects.yaml").read_text())


def roll(tool: str) -> Path:
    out = Path(__file__).parent / "rolls" / tool / f"{time.strftime('%Y%m%d-%H%M%S')}.png"
    return generate_to(out, STYLE.format(subject=SUBJECTS[tool]), aspect="1:1")


if __name__ == "__main__":
    ids = sys.argv[1:] or list(SUBJECTS)
    with ThreadPoolExecutor(4) as pool:
        for p in pool.map(roll, ids):
            print(p)
