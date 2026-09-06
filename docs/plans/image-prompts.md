# Mascot image prompts

## Base style prompt (prepend to every mascot)

> Minimal flat vector illustration of [ANIMAL], geometric shapes, clean bold outlines, limited palette: deep charcoal background (#1a1d21), warm off-white, one accent color per animal, subtle terminal-green (#33ff99) detail as a recurring signature element. Friendly but composed — a capable specialist, not a cartoon sidekick. Centered subject, generous negative space, no text, no gradients, no photorealism, no busy background.

Keep the charcoal background and the green signature detail constant across all eight — that's what makes them read as one family on a LinkedIn feed. Vary only the animal, its pose/prop, and the accent color.

Generate square (1024×1024) for mascots; for og:images either regenerate at 1200×630 with the subject shifted left, or compose in the site build (mascot left, name + tagline right on the charcoal background — more reliable than prompting for layout).

## Per-tool prompts (append the pose to the base)

**biston** (peppered moth) — accent: bark-brown/ash grey.
> …a peppered moth resting on tree bark patterned with faint code-like texture, wings almost blending in, one small terminal-green magnifier revealing the moth's outline against the bark.

**zorilla** (striped polecat) — accent: black & white stripes, hint of acid yellow.
> …a zorilla with bold white dorsal stripes, nose down, sniffing at a row of test tubes; one tube emits faint terminal-green stink lines while the others sit inert.

**gerenuk** — accent: rust/sand.
> …a gerenuk standing tall on hind legs, neck extended, delicately picking one single leaf from a branch full of leaves; the chosen leaf is terminal-green, the rest muted.

**madoqua** (dik-dik) — accent: warm tan.
> …a tiny dik-dik standing alert and perfectly still, ears up, next to an oversized checkmark or traffic light showing a single terminal-green light; composition emphasizes smallness and quiet readiness.

**introspect** — suggested honorary animal: **owl**, accent: midnight blue.
> …an owl peering down into a glowing terminal-green pool of water that reflects rows of tiny log lines back at it.

**ty-find** — suggested honorary animal: **tarsier** (huge eyes, nocturnal spotter), accent: violet.
> …a tarsier with enormous luminous eyes, one long finger pointing precisely at a single terminal-green glowing dot among a field of dim grey dots.

**tyreach** — suggested honorary animal: **octopus**, accent: coral.
> …an octopus with arms extended outward tracing thin lines toward small nodes; reached nodes glow terminal-green, unreached ones stay grey and slightly detached.

**pycoati** — accent: chestnut. Pose TBD once the tool's purpose is settled; default:
> …a coati with its long snout rummaging through a neat stack of layered shapes, lifting one layer to peek underneath, terminal-green light escaping from under the lifted layer.

## Notes

- If the generator supports it, add a negative prompt: text, letters, watermark, gradient background, 3D render, photo.
- Generate 3–4 variants per animal and pick for pose clarity at small size — these must survive being ~120 px tall in a LinkedIn preview and a README badge.
- The honorary animals for ty-find / tyreach / introspect are proposals; if you'd rather keep non-animal tools visually distinct (e.g. abstract glyphs), the family still holds as long as background + green signature stay constant.
