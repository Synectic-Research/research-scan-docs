# DESIGN.md — Research Scan documentation site

The rules this site is written against. Read before editing content.

## Audience

Three readers, in priority order.

1. **AI engineers building agents.** They arrive asking whether `research-scan`
   is a component they can build on. They need the agent/tool boundary, the MCP
   surface, and the file contracts — fast, and without marketing.
2. **Researchers using AI tools.** They arrive asking whether the output can be
   trusted. They need the verification story, the measured results *with their
   caveats*, and the honest "not for" boundaries.
3. **OSS contributors.** They arrive asking how the thing is put together and
   what a good patch looks like. They need the architecture rules and the
   measured-or-reverted gate.

Nobody arrives wanting to be sold to. Every reader is technical.

## The 30-second requirement

A stranger on the introduction page must be able to answer, within 30 seconds:

- **What is it?** An evidence pipeline a reasoning agent drives — it returns a
  verified, ranked shortlist of papers with an argument attached to each.
- **Why two layers?** Because judgement and retrieval have different failure
  modes. The engine is deterministic and auditable; the agent supplies cognition
  under written rubrics. Files are the boundary.
- **How do I run it?** `uvx research-scan doctor`, then drive it from an agent.

If a change to the introduction page makes any of those three harder to find,
the change is wrong.

## Language rules

**Banned outright:**

- "search engine" as a description of the product. It returns a verified ranked
  shortlist with a per-paper argument, not search results.
- "revolutionary", "magic", "autonomous researcher", "AI scientist",
  "replaces …", superlatives, hype of any kind.

**Allowed as ordinary technical description, in body prose only:**

- "evidence-first" as an adjective — *an evidence-first workflow: verify before
  rank*.
- "evidence primitive" in architecture and concepts sections — *can serve as an
  evidence primitive inside larger agent workflows*.

Neither appears in hero copy, and neither is a branded label. They are ordinary
words doing ordinary work.

**Register:** technical, concise, calm. Stripe-grade developer docs are the
target. Short sentences. Concrete nouns. No second-person cheerleading.

**Claims:** capabilities are stated as capabilities. Measured results carry the
argument, and always travel with their eval context — which topics, which judge,
which caveats. A number without its context is not publishable here.

## Grounding rules

- **The main repo is the source of truth.** Where this site and the repo
  disagree, the repo wins and this site is the bug.
- **Every command shown has a verified transcript behind it**, captured from the
  published tool. There is no one-shot `scan` command; do not invent one.
- **Nothing outruns repository reality.** If the repo cannot substantiate a
  claim, state the uncertainty or omit the claim. Never fill a gap by inference.
- **Keep the "not for" boundaries.** Systematic reviews, manuscript citation
  management, and full-text work are explicitly out of scope, and saying so is
  part of the product's honesty.

## Boundary

MCP is **local stdio via `uvx`**. This site documents no hosted endpoint, no
remote transport, no bearer token, no team deployment. That surface was deliberately
dropped from the public project in v0.5.0 and does not exist here.

## Diagrams

Prefer a diagram to a paragraph for: the two-layer split, the pipeline, and the
MCP interaction. Diagrams are hand-authored inline SVG using `currentColor` and
CSS custom properties, so they inherit the theme's light and dark tokens without
a second asset and without a JavaScript dependency.

Every diagram carries a `<title>` for screen readers and stays legible at mobile
width.

## Structure

Pages are dense rather than numerous. A page that would be a stub gets merged
into its neighbour. Fewer, fuller pages beat a padded tree — a sidebar entry
that opens onto three sentences is a broken promise.
