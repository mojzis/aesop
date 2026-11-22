# aesop art style

Every image on the site is a plate from a 19th-century zoology book: fine black ink
line drawing with pen hatching, hand-tinted with delicate watercolour, on plain aged
cream paper. No text, no frame, no props or scenery beyond a perch. That is what makes
the mascots read as one family.

This file is the single source of the style: `art/generate.py` reads the two prompt
templates below (the `text` blocks, in order). Subjects live in `art/subjects.yaml`.

## Plate: one tool, one animal

Square, 1:1. Used as the tool's mascot and its og:image (`pick.sh` → 512×512 webp).

```text
Natural history illustration from a 19th-century zoology book: {subject}. Fine black ink line drawing with pen hatching, hand-tinted with delicate, slightly uneven watercolour washes. Plain aged cream paper background, evenly lit, filling the whole square. One specimen, centred, the whole animal inside the frame with a generous margin. No text, no lettering, no labels, no figure numbers, no border, no frame, no caption.
```

Subject: species with its Latin name, view (side / dorsal / facing), pose, and the
two or three marks that identify it. One sentence.

## Group plate: the menagerie, for the common pages

16:9, used as og:image for pages that are not one tool (home, setup, guide, news;
`pick.sh` → 1200×630 webp). The tools' own plates are passed as reference images, so
the animals look like their mascots.

```text
Natural history illustration from a 19th-century zoology book, a plate showing several species together: {subject}. Each animal drawn exactly as in the reference plates. Fine black ink line drawing with pen hatching, hand-tinted with delicate, slightly uneven watercolour washes. Plain aged cream paper background, evenly lit, filling the whole wide frame. Every animal entirely inside the frame with a generous margin, no overlapping bodies. No text, no lettering, no labels, no figure numbers, no border, no frame, no caption.
```

Subject: which animals and how they are arranged. In `subjects.yaml` a group is a
mapping with `scene` and `refs` (tool ids whose mascots go in as references).

## Workflow

```
uv run --env-file ../cecil/.env art/generate.py [id ...]   # REPLICATE_API_TOKEN; rolls kept in art/rolls/<id>/
art/pick.sh <id> [stamp]                                   # newest roll by default → public/static/img/<id>.webp
```

Roll 2–3 times, pick for clarity at ~120 px (LinkedIn preview, README badge).
