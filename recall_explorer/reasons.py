"""Derive contamination-reason tags from openFDA's free-text reason_for_recall.

openFDA has no reason code list. `reason_for_recall` is free prose written by
the recalling firm, ranging from "Undeclared milk" to full paragraphs.

Tagging is deliberately MULTI-LABEL: a recall that cites both an undeclared
allergen and a foreign object genuinely has two causes, and collapsing that to
one would discard true information. The consequence, which callers must honour:
tag counts do NOT sum to the recall count, so any share computed from these is
"of recalls mentioning X", never "share of all recalls".

Unlike categories.CATEGORY_RULES, order here is NOT load-bearing -- every rule
is evaluated and all matches are returned. Rules are listed roughly by
frequency for readability only.

Rows matching no rule return an empty list; the pipeline surfaces those as
"Other" rather than dropping them.
"""

import re

REASON_RULES = [
    # Allergen and labeling failures -- the largest group by far. Most are
    # phrased as a labeling defect ("does not declare"), not as "allergen".
    ("Undeclared allergen", r"undeclared|allergen|does not declare|not declared|"
                            r"mislabel|misbrand|incorrect label|wrong label|"
                            r"contains statement|label did not|not listed on the label"),

    ("Listeria", r"listeria"),
    ("Salmonella", r"salmonella"),
    ("E. coli", r"e\.\s*coli|\becoli\b|escherichia|stec\b|o157"),

    ("Foreign material", r"foreign (material|object|matter)|metal fragment|"
                         r"pieces of (metal|plastic|glass|rubber|wire|wood)|"
                         r"extraneous material|\bglass\b|insect|rodent"),

    ("Botulism risk", r"botul|clostridium"),
    ("Other pathogen", r"hepatitis|norovirus|cyclospora|cronobacter|"
                       r"staphylococc|burkholderia|\bmold\b"),

    ("Chemical/contaminant", r"pesticid|herbicid|chloramphenicol|heavy metal|"
                             r"\blead\b|arsenic|cadmium|cesium|melamine|"
                             r"microcystin|unapproved (ingredient|additive|color)"),

    ("Processing/temperature", r"underprocess|under-process|process deviation|"
                               r"temperature abuse|not held at an appropriate temperature|"
                               r"pasteuri|insanitary|haccp|\bcgmp\b|\bgmp\b"),
]


# Derived, not hand-copied -- the reason filter's option list must stay in
# sync if a rule is ever added to REASON_RULES above.
REASON_LABELS = [label for label, _pattern in REASON_RULES]


def tag_reasons(reason_text):
    """Return every reason label whose pattern appears in the text.

    Multi-label by design -- see module docstring. Returns [] when nothing
    matches, which callers render as "Other".
    """
    text = (reason_text or "").lower()
    return [label for label, pattern in REASON_RULES if re.search(pattern, text)]
