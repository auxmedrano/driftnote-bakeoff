# Does more planning produce better results?

Same landing-page brief as the main bake-off, same hardware, same four
models. Three conditions, isolating two different things people mean by
"planning":

- **A — No planning (baseline).** One-shot generation, `think=false`
  (`think=low` for gpt-oss, which has no true "off" state). This reuses the
  bake-off's original runs.
- **B — Internal reasoning.** Identical one-shot prompt, `think=high`/`true`
  — the model plans silently in a `<think>` block (or the CLI's
  `Thinking…done thinking` equivalent) before writing code.
- **C — Explicit external planning.** Two separate calls: first the model
  writes a structured design plan in plain text (palette with named roles,
  section-by-section layout at three widths, accordion interaction logic,
  an accessibility checklist), then that plan is fed back as context in a
  second prompt asking for the implementation. Both calls use `think=false`
  (`think=low` for gpt-oss), so the only variable versus baseline is
  *whether a plan was written down first* — not extra internal reasoning.

## Scoring

A fixed 23-item structural checklist against the brief (header, hamburger
breakpoint, hero CTA, 3+ features, 2+ pricing tiers with one marked
recommended, FAQ with a real single-open accordion, dark mode + working
persisted toggle, semantic elements, keyboard-operable controls, aria
coverage, zero external deps, balanced tags) — see `score.py`. Also tracks
raw `@media` rule count as a secondary thoroughness signal (not itself a
"more is better" metric, but informative).

**Important caveat on the checklist's reliability:** four rounds of manual
verification against the actual generated markup caught real false
negatives in the first draft of the rubric — a `767.98px` breakpoint that a
`\d+px` regex didn't match, a reasoning-model transcript where the
extractor grabbed a stray code sketch from inside `<think>` instead of the
real answer, a correct single-open accordion implemented via a named
`closeItem()` helper that an inline-pattern regex missed, and three cases
where gpt-oss used equally-valid alternate conventions (`position:fixed`
instead of `sticky`, `class="card"` instead of `class="feature"`, and
`aria-expanded`+`aria-controls` on a button without the literal words
"faq"/"accordion" nearby). All four were fixed in `score.py` and everything
was rescored. One flagged miss was manually confirmed as a genuine defect
(gemma4:latest's baseline hamburger toggle is a `<div>` with no
`tabindex`/keydown handling — real, not a scoring artifact). Treat the
scores below as a reasonably solid signal, not a certified grader.

## Results

| Model | Condition | Score | Time | Tokens | `@media` rules |
|---|---|---|---|---|---|
| `qwen3.8-27b-q3` | A — baseline | 23/23 | 6m 41s | 11,265 | 8 |
| `qwen3.8-27b-q3` | B — internal reasoning | 23/23 | 20m 37s | 32,440 | 12 |
| `qwen3.8-27b-q3` | C — explicit plan | 23/23 | 8m 9s (1,982 + 11,465) | 10 |
| `gpt-oss:20b` | A — baseline | 20/23 | 28.4s | 2,457 | 3 |
| `gpt-oss:20b` | B — internal reasoning | **23/23** | 4m 27s | 24,656 | 6 |
| `gpt-oss:20b` | C — explicit plan | **23/23** | **49.0s** | 1,474 + 2,915 | 11 |
| `gemma4:latest` | A — baseline | 22/23 | 1m 28s | 6,172 | 3 |
| `gemma4:latest` | B — internal reasoning | 23/23 | 1m 33s | 6,588 | 5 |
| `gemma4:latest` | C — explicit plan | 23/23 | 2m 4s (1,325 + 7,350) | 5 |
| `gemma4:12b` | A — baseline | 23/23 | 1m 27s | 4,270 | 3 |
| `gemma4:12b` | B — internal reasoning | 23/23 | 2m 5s | 6,268 | 2 |
| `gemma4:12b` | C — explicit plan | 23/23 | 2m 8s (1,239 + 5,065) | 3 |

## Findings

**"More planning" only helps where there's a gap to close.** `qwen3.8-27b-q3`
and `gemma4:12b` both started at 23/23 in baseline — neither planning
condition could improve the checklist score further (ceiling effect). Only
`gpt-oss:20b` (20/23) and `gemma4:latest` (22/23) had real gaps, and both
conditions closed them for both models.

**Explicit planning beat internal reasoning on cost-effectiveness, at least
for gpt-oss:20b.** Condition C reached the identical 23/23 outcome as
Condition B for ~5.5x less wall-clock time (49.0s vs. 4m27s) and ~5.7x
fewer tokens (4,389 vs. 24,656 total). Writing a plan down and handing it
back as context was nearly free next to making the model "think harder"
about the same one-shot prompt.

**For models already at the ceiling, more planning showed up as depth, not
correctness — and not consistently.** `qwen3.8-27b-q3`'s breakpoint count
tracked the planning intensity (baseline 8 → explicit-plan 10 → internal-
reasoning 12), suggesting internal reasoning specifically bought more
responsive-design granularity here. `gemma4:12b` showed the opposite for
internal reasoning — breakpoints *dropped* from 3 to 2 under Condition B,
while Condition C exactly matched baseline (3). More internal reasoning
did not reliably mean a more thorough artifact across models; it helped
qwen's depth and didn't help (arguably slightly hurt) gemma4:12b's.

**Internal reasoning is the expensive lever for a big model.**
`qwen3.8-27b-q3` under Condition B took 20m37s and 32,440 tokens — 3.1x
the baseline's time for a checklist score that didn't move (already at
ceiling) and a real but modest depth gain (+4 breakpoints). For a model
this slow per-token, "think harder" is a costly way to buy incremental
polish.

**Bottom line for this brief, on this hardware:** if a model already meets
the checklist one-shot, don't bother planning further — you're paying for
depth you may not need. If it doesn't, an explicit written plan is a far
cheaper way to close the gap than cranking up internal reasoning effort,
at least for the one model (gpt-oss:20b) where both conditions started
from the same real deficit.

## A human spot-check, and why qwen's C looks different from A and B

The checklist maxes out at 23/23 for all three `qwen3.8-27b-q3` conditions,
so it has nothing left to say about which one is actually *better* — that
needs an eye, not a regex. On visual review, B was ranked the best of the
three, with C second and A last.

That ranking is at least directionally consistent with the one thing the
checklist *can* still measure once everyone's at the ceiling: breakpoint
depth track the same order (B 12 → C 10 → A 8, see Findings above). But it
comes at B's real cost — 20m37s versus C's 8m9s and A's 6m41s — which the
"explicit planning is the cheap win" conclusion above (drawn from gpt-oss)
does not straightforwardly extend to. For qwen specifically, the expensive
lever seems to have bought something real.

Separately, a visual question came up: why do A and B *look* so similar
(same warm-cream-and-terracotta family) while C looks different (cooler,
green-accented)? The actual token values settle it:

| Condition | Background | Accent |
|---|---|---|
| A | `#f6f1e6` | `#cf4a2b` |
| B | `#f3efe4` (near-identical to A) | `#c93d12` (same red-orange family as A) |
| C | `#F7F5F0` (cooler, less saturated) | `#2F6B5E` (teal-green — a different hue family entirely) |

A and B are both **one-shot completions of the literal same prompt text**
— same model, same instruction, no intermediate step — so the model's
"instinct" for this exact brief converges on nearly the same palette both
times (this is also the same warm-cream/terracotta default flagged as a
common AI-aesthetic cliché in the main bake-off). C's palette differs
because C *is not the same prompt*: it's the output of a separate
plan-writing call, worded differently (explicitly asking the model to name
and justify each color token's role, one sentence at a time), whose output
is then fed back as context for a second build call. That's a genuinely
different prompt conditioning a fresh sampling draw — not evidence that
"explicit planning" as a general mechanism produces different color
choices, just that *this specific* differently-worded planning prompt did.
`think=high` (Condition B), by contrast, reasons about the *same* original
prompt, so it isn't surprising its color choice landed close to baseline's.

## Files

- `plan-prompt.txt` — the planning-step prompt (Condition C, step 1)
- `build-prompt-template.txt` — the implementation-step template (Condition
  C, step 2), with `{PLAN}` substituted per model
- `<model>.plan.txt` — each model's actual written plan (Condition C output)
- `<model>.condB.html` / `<model>.condC.html` — each model's HTML output
  per condition (raw transcripts alongside as `.raw.txt`)
- `score.py` — the scoring rubric (see caveat above)
- `extract.py` — shared code-block extractor, handles both `<think>` and
  the CLI's `Thinking…done thinking` marker formats
