# Final Food-Recall Classification Taxonomy — v2 (revised per Mai's feedback)

This revises `scratch/taxonomy_proposal.md` (the raw Opus 5 output) against
four corrections Mai made after reviewing it. All four are the same move:
group by **composition** (what it's made of) rather than by **destination**
(where it's consumed) or by **exclusion** (grouped with things it merely
isn't). No new API call — these are precise re-groupings of rows the first
call already examined and cited; the evidence doesn't change, only which
label it lands in.

---

## What changed vs. v1

| # | v1 (Opus 5 proposal) | v2 (Mai's correction) |
|---|---|---|
| 1 | Protein powders and RTD shakes → `Supplements`, regardless of protein source | **Plant-protein-based powders/shakes (pea, soy, rice, hemp isolate) → `Plant Protein`.** Whey, casein, collagen, and blended/animal-derived powders and shakes stay `Supplements`. |
| 2 | Plant milks → `Beverages` | **Plant milks → `Plant Protein`** (oat, almond, soy, rice, cashew, coconut-milk beverages) |
| 3 | Pet food/treats → `Non-Food Item` | **New label: `Pet Food/Treats`**, split out of `Non-Food Item` |
| 4 | All coffee creamer → `Beverages` | **Two-way split**: dairy creamer → `Dairy`; everything else, including plant-based creamer (oat, soy, almond base), → `Beverages`. Plant-based creamer does **not** follow plant milk into `Plant Protein` — see correction note below. |

**Rationale Mai gave, generalized:** v1's own §3 header ("New collisions
found") states the right principle for plant analogs — *classify by what
they are made of, not what they imitate* — and applied it correctly to
plant-based meat, egg, and cheese analogs (→ `Plant Protein`). It then
didn't apply the same principle to plant milk or plant-based protein
powder, routing both by destination (`Beverages`, `Supplements`) instead.
v2 fixes that for plant milk and protein powder: if a plant-based food's
animal counterpart is Dairy or Meat, and the product is itself
protein-bearing, the plant version is `Plant Protein` — mirroring how
dairy milk itself sits in `Dairy` (composition) rather than `Beverages`
(how it's consumed).

**Correction (this pass) — plant-based coffee creamer does not follow
plant milk.** The composition principle only applies when the product
actually *is*, compositionally, the plant-protein food in question. Checked
against v1's own cited evidence (§ Coffee creamer → Beverages, all examples
are branded products: Coffee-Mate, Silk, International Delight, MO-CHA,
Kraft, Libby's) — none of it examined ingredient or protein content, it
only used inconsistent keyword-labeling of near-identical products as the
reason to standardize on `Beverages`. Real plant-based coffee creamer
(Silk, Coffee-Mate Natural Bliss, etc.) is typically water, oil (often
coconut/sunflower, not the named plant milk), sugar, and thickeners/
emulsifiers — an additive product, not a protein-bearing food; label
protein is usually 0g/serving. That's a different composition from
oat/soy/almond *milk* itself, sold and consumed as the primary
beverage/food. So plant milk stays in `Plant Protein`, but plant-based
creamer reverts to the fallback `Beverages` rule alongside dairy-free
creamer generally — only dairy creamer gets pulled out, to `Dairy`.

Pet food is a different kind of fix: v1 grouped "not meant for human
consumption" with "not food at all," which conflates an edible product
(subject to real food-safety recalls — salmonella, foreign material) with
inedible objects (cookware, cosmetics). Splitting it out doesn't change any
row's evidence, just gives it a label that means what it says.

---

## Final label set (21)

The log's 18, plus `Eggs`, `Baby/Toddler Food`, and `Pet Food/Treats`.
`Plant Protein`'s scope is the biggest mover — see below.

| # | Label | Status vs. the log's 18 |
|---|---|---|
| 1 | **Dairy** | Changed (v1) — absorbs flavored milk, egg nog, cheese-based dips, bulk dairy commodity powders; **v2 adds:** dairy-based coffee creamer explicitly. Loses infant formula to `Baby/Toddler Food`. |
| 2 | **Eggs** | New (v1) |
| 3 | **Beef/Pork/Poultry/Game Meats** | Changed in scope, not name (v1) — excludes eggs, meat-named seasonings, buns, sandwiches, broths, plant analogs |
| 4 | **Seafood** | Clarified (v1) |
| 5 | **Produce** | Clarified (v1) — fresh herbs in, dried herbs out; packing medium never governs |
| 6 | **Plant Protein** | Changed (v1) — gains vegan meat/egg/cheese analogs. **v2 expands:** also gains plant milks and plant-protein-based powders/RTD shakes (pea, soy, rice, hemp). **Not** plant-based coffee creamer — see correction note above; that stays with `Beverages`/`Dairy`. Loses nothing to Supplements that is plant-sourced. |
| 7 | **Grains/Cereal** | Unchanged |
| 8 | **Bakery** | Unchanged (absorbs bun rows mislabeled `Beef`) |
| 9 | **Prepared/Frozen** | Changed (v1) — gains liquid broth/stock, dressed pasta/potato deli salads, non-dairy frozen desserts |
| 10 | **Snacks/Candy** | Unchanged |
| 11 | **Nuts/Seeds** | Unchanged |
| 12 | **Beverages** | Changed (v1) — gains alcoholic beverages, cocktail mixers/syrups. **v2 narrows:** loses plant milk to `Plant Protein`. Coffee creamer stays here as the fallback (dairy creamer alone moves to `Dairy`) — plant-based creamer stays `Beverages` too, since it's compositionally an additive product, not a protein-bearing plant-milk food. |
| 13 | **Spices/Condiments** | Changed (v1) — gains honey, liquid sweeteners, meat-named rubs/marinades, bouillon/soup bases |
| 14 | **Oils/Fats** | Confirmed and bounded (v1) |
| 15 | **Supplements** | Changed (v1) — gains medical foods, enteral formulas, claim-bearing honey, kratom, protein powders/RTD shakes. **v2 narrows:** only non-plant (whey/casein/collagen/blended/animal-derived) protein powders and shakes stay here; plant-based ones move to `Plant Protein`. |
| 16 | **Baking Supplies** | Unchanged (dry-sugar vs. liquid-sweetener test) |
| 17 | **Food Additives/Ingredients** | Changed (v1) — gains creamer stabilizer systems, nitrite cures, bulk purified sweeteners |
| 18 | **Non-Food Item** | Changed (v1: gains pet food, cosmetic/oral-care kits). **v2 narrows:** loses pet food/treats to its own label — this label is now strictly inedible objects (cookware, tableware, cosmetics, decorative items). |
| 19 | **Baby/Toddler Food** | New (v1) — infant/toddler purees, pouches, cereal, and all infant formula regardless of protein base |
| 20 | **Pet Food/Treats** | **New (v2)** — dog/cat/other pet food, treats, chews, and supplements sold as pet products. Same recall-hazard logic as `Baby/Toddler Food` (a real food-safety category, just not for humans) rather than lumping with inedible objects. |
| 21 | **Uncategorized** | Unchanged |

---

## Revised rule text for the affected labels

**Plant Protein** (supersedes v1's scope for this label) — Beans and
legumes in all forms, including cooked bean dishes; soy protein isolates
and concentrates, textured vegetable protein, tofu, bean curd, edamame,
lentils, chickpeas; hummus and other legume-based dips and spreads;
veggie/black-bean burgers; **plant-based meat, egg, cheese, and yogurt
analogs** (Impossible, Just Egg, vegan cheese, dairy-free pudding);
**plant milks** (oat, almond, soy, rice, cashew, coconut-milk beverages);
and **plant-protein-based protein powders and RTD shakes** (pea, soy, rice,
hemp isolate — scoop-format or ready-to-drink, marketed as a supplement or
not). The unifying test: if the product's identity is defined by a plant
protein or plant-milk base, it goes here regardless of what it's
substituting for or how it's packaged/marketed. **Plant-based coffee
creamer is explicitly excluded** — see `Beverages` below; a creamer is
overwhelmingly oil/thickener/sugar with only a token plant-milk fraction,
not a protein-bearing food in its own right.

**Supplements** (narrows v1's protein-powder addition) — Vitamins,
minerals, capsules, tablets, softgels, digestive enzymes, probiotics,
colostrum, herbal extracts, weight-loss drops, energy gels, pre-workout,
medical foods and enteral/oral nutritional formulas sold to consumers,
dysphagia-thickened beverages, claim-bearing honey sachets (performance/
therapeutic claims), kratom. **Protein powders and RTD shakes stay here
only when the protein source is animal-derived or blended/non-plant**
(whey, casein, collagen, egg-white protein, or a whey/plant blend where
plant isn't the sole or dominant source) — plant-only sources go to
`Plant Protein` instead (see above).

**Dairy** (adds explicit creamer line; otherwise unchanged from v1) —
...as v1, plus: **dairy-based coffee creamer** (cream-, milk-, or
half-and-half-based, including flavored varieties) is `Dairy`.

**Beverages** (narrows v1's creamer addition) — Soda, juice, water, coffee,
tea, drink mixes, coffee pods, alcoholic beverages (beer, wine, cider,
spirits, hard seltzer, RTD cocktails), non-alcoholic cocktail mixers and
drink syrups/concentrates. **Coffee creamer is Beverages by default** —
liquid or powdered, dairy-free or plant-based (oat, soy, almond, cashew),
synthetic non-dairy (oils, starches, sodium caseinate/casein derivatives).
Only **dairy-based** creamer (cream-, milk-, or half-and-half-based)
carves out to `Dairy`; plant-based creamer stays here, unlike plant milk
itself — see the `Plant Protein` correction note above for why the two
aren't treated the same.

**Non-Food Item** (narrows v1; pet food removed) — Not intended for human
or animal consumption: cookware, pots, knives, utensils, plates, cups,
serving trays, bakeware, cosmetics, hair products, tooth powder, decorative
pigments, oral-care and cosmetic kits. Pet food and treats are **not** here
— see the new `Pet Food/Treats` label.

**Pet Food/Treats** (new) — Food, treats, chews, and dietary supplements
manufactured and sold for animal (not human) consumption: dog food, cat
food, pet treats, pet chews, pet vitamins. Distinct from `Non-Food Item`
because it is genuinely food — subject to the same class of recall hazards
(*Salmonella*, foreign material, nutritional deficiency) as any other food
label, just not for people.

**Baby/Toddler Food** — unchanged from v1 (see `scratch/taxonomy_proposal.md`
for full rule and evidence; not affected by these four corrections).

**Eggs, Beef/Pork/Poultry/Game Meats, Seafood, Produce, Grains/Cereal,
Bakery, Prepared/Frozen, Snacks/Candy, Nuts/Seeds, Spices/Condiments,
Oils/Fats, Baking Supplies, Food Additives/Ingredients, Uncategorized** —
unchanged from v1; see `scratch/taxonomy_proposal.md` for full rules,
boundaries, and cited evidence.

---

## Everything else from v1 stands unrevised

The four open-question resolutions (Eggs, plain milk/produce/meat, Oils/Fats,
full relabel), the six coverage-hole rules (alcohol, broth, baby food, honey,
agave/stevia/molasses — coffee creamer is superseded above), and 7 of the 8
new collisions (meat-named seasonings, deli sandwiches, dressed deli salads,
hummus/dips boundary, medical/enteral nutrition, non-food items) carry over
from `scratch/taxonomy_proposal.md` without change. Only the "plant analogs"
collision (§3 in v1) and its plant-milk/creamer sub-rule are superseded by
this document.
