---
name: extract-synthesis-recipe
description: Extracts materials-synthesis recipes from free-form text (papers, abstracts, lab notes) into a strict JSON schema. Use when the user asks to parse, extract, or structure synthesis information, or wants to convert experimental procedures into machine-readable form.
when_to_use: Synthesis extraction tasks, parsing methods sections, building synthesis databases, populating reconstruction or simulation configs from prose.
allowed-tools: Read
---

# Extract Synthesis Recipe

## Task

Read the text the user provides (or a file they point to) and extract every
distinct synthesis procedure as a JSON record with the schema below. If the
text contains multiple recipes, return a JSON array; otherwise return a
single object.

## Output schema

```json
{
  "material":            "string  (chemical formula)",
  "route":               "sol-gel | solid-state | hydrothermal | co-precipitation | CVD | other",
  "precursors":          ["array of strings"],
  "calcination_temp_C":  "number | null",
  "calcination_time_h":  "number | null",
  "atmosphere":          "string | null",
  "crystallite_size_nm": "number | null",
  "confidence":          "high | medium | low",
  "evidence_quote":      "verbatim quote from the source supporting the extraction",
  "extraction_notes":    "string | null  (use to flag ambiguities or missing fields)"
}
```

## Rules

1. **Never invent values.** If a field is not stated in the text, set it to
   `null` and lower `confidence`.
2. **Quote the evidence.** `evidence_quote` must be a verbatim substring of
   the source — do not paraphrase.
3. **Flag non-syntheses.** If the passage is not actually a synthesis (e.g.
   a modelling paper, an instrumentation description), do **not** invent a
   record. Instead, return a single object with `confidence: "low"` and
   `extraction_notes` explaining why.
4. **Preserve units.** Convert "overnight" → null + a note; do not guess "8 h".
5. **Chemistry is verbatim.** Keep formula casing/subscripts as written
   (`BaTiO3` not `batio3`).

## Validation checklist (run mentally before returning)

- [ ] Did I quote evidence for *every* non-null field?
- [ ] Did I refuse to fabricate values for missing fields?
- [ ] Did I flag any decoy passages with `confidence: low`?
- [ ] Is the JSON parseable (no trailing commas, double quotes only)?

## Output

Return only the JSON. No commentary, no markdown fences. The user's pipeline
will parse your response directly.
