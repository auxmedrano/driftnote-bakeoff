# Driftnote landing page — model bake-off results

Same prompt (`prompt.txt`), same hardware (AMD RX 9070 XT, 16GB VRAM, Ollama
0.32.14, ROCm), each model run independently via direct `ollama run` CLI
calls — no MCP tooling in the loop, no worker-imposed timeout.

| Model | Quant | Output size | Tokens generated | Wall time | Gen speed | `@media` breakpoints | `aria-*` attrs | `<footer>` | `prefers-reduced-motion` |
|---|---|---|---|---|---|---|---|---|---|
| `qwen3.8-27b-q3` | Q3_K_L (3-bit) | 33.4 KB | 11,265 | 6m 41s | 28.1 tok/s | 8 | 42 | Yes | Yes |
| `gpt-oss:20b` | MXFP4 | 7.9 KB | 2,457 | 28.4s | 100.6 tok/s | 3 | 18 | No | Yes |
| `gemma4:latest` | Q4_K_M | 23.6 KB | 6,172 | 1m 28s | 73.6 tok/s | 3 | 37 | Yes | No |
| `gemma4:12b` | Q4_K_M | 16.3 KB | 4,270 | 1m 27s | 51.6 tok/s | 3 | 10 | Yes | No |

All four outputs are well-formed (verified: every `<html>`/`<head>`/`<body>`/
`<style>`/`<script>`/`<header>`/`<nav>`/`<section>`/`<footer>` tag balanced)
and satisfy the letter of the brief. What differs is scope and polish:

- **`qwen3.8-27b-q3`** wrote by far the most complete implementation —
  8 independent breakpoints (hero/features/pricing/footer/nav each handled
  separately), the most `aria-*` coverage, `prefers-reduced-motion` support,
  and a synchronous head-script theme loader that avoids flash-of-wrong-theme
  entirely. Slowest by a wide margin (6m41s) — a real cost for that scope at
  this quant's ~28 tok/s.
- **`gpt-oss:20b`** was the fastest by ~2.5x over the next fastest, but also
  the smallest and least complete output — it skipped the footer entirely and
  used only 3 breakpoints total (one shared cutoff rather than per-section
  tuning).
- **`gemma4:latest`** landed a strong middle ground: fast (73.6 tok/s),
  reasonably complete (37 `aria-*` attrs, has a footer), but no
  `prefers-reduced-motion` handling.
- **`gemma4:12b`** (the multimodal variant) was the slowest of the three
  small/mid models and had the thinnest accessibility coverage (10 `aria-*`
  attrs) despite being a larger, vision-capable model than `gemma4:latest`.

None of the four used identical color palettes or fonts — see each file's
`<style>` block. `qwen3.8-27b-q3` reached for a warm-cream/serif/terracotta
combination that's a well-known "default AI aesthetic" pattern; the others
picked distinct blue/indigo-leaning palettes.

## Dark-theme follow-up (qwen3.8-27b-q3 only)

Human review flagged `qwen3.8-27b-q3`'s dark theme as noticeably weaker than
its light theme. Checking the actual WCAG contrast ratios showed this
wasn't an accessibility defect — dark mode measured *higher* contrast than
light mode on every text/background pair (body text 15.75:1 vs. 14.61:1;
accent text 5.93:1 vs. 3.99:1). The problem was color harmony: the accent
was brightened and re-saturated for dark mode (`#cf4a2b` → `#f4623f`)
rather than desaturated, reading as hot/neon against the warm brown-black
background instead of calm and considered.

We asked `qwen3.8-27b-q3` to regenerate *only* the
`html[data-theme="dark"]{...}` token block, supplying the light-theme block
as a working reference and the harmony critique above as the brief, with
explicit contrast-ratio floors (body text >7:1, accent text >4.5:1, button
text >4.5:1). One shot, 9.7s, no page regeneration needed. Result:
`--accent:#f4623f` → `#e29471` (muted salmon) and `--accent-2:#63b096` →
`#7a9c8e` (muted sage) — it desaturated `--accent-2` too, unprompted,
applying the same principle consistently. New contrast: accent text on
background 7.75:1, button text on accent 7.66:1 — both improved, not just
maintained. The fix is now live in `qwen3.8-27b-q3.html`; the original
values were `--accent:#f4623f; --accent-ink:#1a120e; --accent-2:#63b096;`
(see git history for the pre-fix version). Full transcript:
`qwen-dark-theme-fix.raw.txt`.

## Does more planning produce better results?

Separate follow-up experiment: all four models re-run under internal
reasoning (`think=high`) and under an explicit two-step plan-then-build
workflow, scored against a fixed 23-item checklist. See
[`planning-experiment/results.md`](planning-experiment/results.md).
Headline finding: for `gpt-oss:20b`, an explicit written plan reached the
same perfect score as heavy internal reasoning at ~5.5x less wall-clock
time.

## Files

- `prompt.txt` — the exact prompt sent to every model
- `<model>.html` — each model's raw output (dark-mode accent in
  `qwen3.8-27b-q3.html` has one targeted fix applied — see above)
- `<model>.raw.txt` — the full CLI transcript (includes `--verbose` timing
  stats) each `.html` file was extracted from
- `qwen-dark-theme-fix.raw.txt` — transcript of the isolated dark-theme
  regeneration described above
