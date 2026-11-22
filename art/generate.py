# /// script
# requires-python = ">=3.12"
# dependencies = ["imgen", "pyyaml"]
# [tool.uv.sources]
# imgen = { path = "../../imgen", editable = true }
# ///
"""Generate mascot plates. Every roll is kept in art/rolls/<id>/<stamp>.png.

    uv run --env-file ../cecil/.env art/generate.py [id ...]   # REPLICATE_API_TOKEN

Style and prompt templates: art/STYLE.md. Pick a roll with art/pick.sh <id> <stamp>.
"""

import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
from imgen import generate_to  # ty: ignore[unresolved-import]  -- PEP 723 dep, not in the venv

ART = Path(__file__).parent
IMG = ART.parent / "public" / "static" / "img"
# The two prompt templates (plate, group plate) are the ```text blocks in STYLE.md.
PLATE, GROUP = re.findall(r"```text\n(.*?)\n```", (ART / "STYLE.md").read_text(), re.S)
SUBJECTS = yaml.safe_load((ART / "subjects.yaml").read_text())


def roll(tool: str) -> Path:
    out = ART / "rolls" / tool / f"{time.strftime('%Y%m%d-%H%M%S')}.png"
    subject = SUBJECTS[tool]
    if isinstance(subject, str):
        return generate_to(out, PLATE.format(subject=subject), aspect="1:1")
    refs = [IMG / f"{r}.webp" for r in subject["refs"]]
    return generate_to(out, GROUP.format(subject=subject["scene"]), aspect="16:9", refs=refs)


if __name__ == "__main__":
    ids = sys.argv[1:] or list(SUBJECTS)
    with ThreadPoolExecutor(4) as pool:
        for p in pool.map(roll, ids):
            print(p)
