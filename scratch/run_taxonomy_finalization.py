"""Throwaway script: Step 1 taxonomy-finalization API call.

Not checked in. Loads scratch/design_sample.csv and scratch/decision_log.md,
builds the finalization prompt, and asks Opus 5 to propose the final label
set, resolve the four open questions, and write rules for the coverage-hole
product types. Writes the raw response to scratch/taxonomy_proposal.md for
review -- nothing under recall_explorer/ or the repo root is touched.
"""

import csv

import anthropic

TASK_WRAPPER = """\
You are finalizing a food-recall classification taxonomy. The document above
is a decision log recovered from a prior manual classification pass -- it is
your specification, not a prompt to follow verbatim. Your job is to pressure-
test it against a larger, more representative sample and produce the final
version.

Attached below is a CSV sample of {n} rows (recall_number, product_description,
sample_reason). `sample_reason` tells you why each row was included:
- `exhaustive:<category>` -- ALL rows currently keyword-labeled as one of the
  five categories the decision log had zero evidence for (Poultry/Eggs, Pork,
  Beef, Plant Protein, Oils/Fats).
- `coverage_hole:<type>` -- rows matching a product type the log never
  addressed (alcohol, coffee_creamer, broth, baby_food, honey,
  agave_stevia_molasses).
- `stratified:<category>` -- a proportional random sample from the eleven
  other large keyword categories.

Do the following:

1. Apply the decision log's existing rules to every sampled row (mentally --
   you do not need to output a per-row classification). Note where the rules
   worked cleanly and where they broke down.

2. Resolve the four open questions from the log's "Known gaps" section, using
   the sample's actual evidence rather than guessing:
   - Question 1 (eggs): the `exhaustive:Poultry/Eggs` rows are your evidence.
     State whether to add a separate `Eggs` label, and if so, write its rule
     and its boundary against the meat label.
   - Question 2 (plain milk/produce/meat cuts): now covered by the stratified
     sample -- confirm whether the existing rules handle them or need
     adjustment.
   - Question 3 (Oils/Fats): the `exhaustive:Oils/Fats` rows are your
     evidence -- confirm or revise the rule, including its boundary against
     Spices/Condiments (infused oils, oil-based dressings).
   - Question 4 (taxonomy reconciliation): confirm the recommendation to
     relabel the entire dataset under the new taxonomy rather than mapping
     old labels forward.

3. Write a rule (category assignment + one-line rationale) for each of the
   six coverage-hole product types: alcohol, coffee creamer, broth/stock/
   bouillon, baby food (non-formula purees), honey, and agave/stevia/
   molasses. Use the `coverage_hole:*` rows as evidence. Decide whether each
   needs a new label or fits inside an existing one.

4. Flag any further label collisions this larger sample exposes, beyond the
   10 documented boundary rules -- name the specific rows or product types
   that caused the collision.

5. Produce the final candidate label set. Expected size is 19 or slightly
   more (the log's 18 plus `Eggs`, unless your analysis says otherwise). For
   every change versus the log's original 18-label set, give a one-line
   rationale.

## Output format

Write your response as a markdown document with these sections, in order:

### Final label set
The complete list, with a one-line description of what changed from the
log's 18 labels (or "unchanged" for labels that didn't move).

### Open question resolutions
One subsection per question (1-4 above), each with your resolution and the
evidence from the sample that supports it.

### Coverage-hole rules
One rule per product type (alcohol, coffee creamer, broth/stock/bouillon,
baby food, honey, agave/stevia/molasses).

### New collisions found
Any label boundary problems the sample exposed that the log's 10 boundary
rules don't cover. If none, say so explicitly.

### Summary table
A markdown table: label name | row count in this sample | is this a new/
changed/unchanged label vs. the log's 18.

Do not invent statistics you cannot support from the attached sample. If the
sample is too small to confirm something, say so rather than guessing.
"""


def load_decision_log():
    with open("scratch/decision_log.md") as f:
        return f.read()


def load_sample_csv():
    with open("scratch/design_sample.csv") as f:
        return f.read()


def count_rows(csv_text):
    return sum(1 for _ in csv.reader(csv_text.splitlines())) - 1


def main():
    decision_log = load_decision_log()
    sample_csv = load_sample_csv()
    n_rows = count_rows(sample_csv)

    system_prompt = decision_log + "\n\n---\n\n" + TASK_WRAPPER.format(n=n_rows)

    user_content = (
        "Here is the design sample CSV "
        f"({n_rows} rows, columns: recall_number,product_description,category,sample_reason):\n\n"
        f"```csv\n{sample_csv}\n```"
    )

    client = anthropic.Anthropic()

    print(f"Calling Opus 5 with {n_rows} sample rows...")
    with client.messages.stream(
        model="claude-opus-5",
        max_tokens=48000,
        system=system_prompt,
        output_config={"effort": "high"},
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        response = stream.get_final_message()

    print("\n\n--- usage ---")
    print(response.usage)

    proposal_text = next(
        (b.text for b in response.content if b.type == "text"), ""
    )
    with open("scratch/taxonomy_proposal.md", "w") as f:
        f.write(proposal_text)
    print("\nwrote scratch/taxonomy_proposal.md")


if __name__ == "__main__":
    main()
