# Food Recall Classification Rules

The approved taxonomy for the Phase 5 full-dataset LLM reclassification.
This document is the classification spec, the provenance record, and (per
`classify_all.py`, Step 2) the core of the classification prompt's system
block.

**Provenance.** Originates from a manual classification pass over the
3,554-row `Uncategorized` residual (12.2% of the dataset), which produced an
18-label taxonomy and a self-flagged list of gaps (no evidence for eggs,
oils/fats, or plain poultry). That taxonomy was pressure-tested against a
~5,000-row design sample (all 466 rows from the five categories with zero
prior evidence, plus keyword-targeted coverage-hole sampling, plus
proportional stratified sampling across the rest) via a Claude Opus 5 API
call. The API's proposal added `Eggs` and `Baby/Toddler Food`, resolved six
coverage-hole product types, and flagged eight new label collisions. Mai
then corrected four of the API's calls where it classified by destination
or by exclusion instead of by composition — see "Revision history" at the
end of this document.

**Final label count: 21.**

---

## 1. Label set (21)

```text
Dairy
Eggs
Beef/Pork/Poultry/Game Meats
Seafood
Produce
Plant Protein
Grains/Cereal
Bakery
Prepared/Frozen
Snacks/Candy
Nuts/Seeds
Beverages
Spices/Condiments
Oils/Fats
Supplements
Baking Supplies
Food Additives/Ingredients
Non-Food Item
Baby/Toddler Food
Pet Food/Treats
Uncategorized
```

---

## 2. Governing principle

> Classify what the product **most fundamentally is**, not every ingredient
> it contains — and classify by what it **is made of**, not by where it's
> consumed or what it's grouped with by exclusion.

An ice cream product containing nuts is `Dairy`, not `Nuts/Seeds`. A
cheddar party mix is `Snacks/Candy`, not `Dairy`. Plant-based meat, egg,
cheese, and yogurt analogs are classified by their actual plant-protein
composition, not by what animal product they imitate. Pet food is
genuinely food — subject to real food-safety recalls — and is not grouped
with inedible objects merely because it isn't for humans.

When nothing in the description reliably indicates a category, use
`Uncategorized` rather than guessing.

---

## 3. Category rules

**Dairy** — Milk, cheese of all kinds, cream, butter, yogurt, ice cream,
sherbet, gelato, frozen custard, half-and-half, paneer, quark, mascarpone.
Flavored milk (chocolate, strawberry) is `Dairy`, not `Beverages` or
`Snacks/Candy`. Egg nog is `Dairy` — it is an overwhelmingly milk-and-cream
dairy-plant product; the word "egg" in the name is not the product. Cheese-
and cream-cheese-based dips and spreads (pimento cheese dip, cheese balls,
queso made primarily of cheese) are `Dairy`. Bulk dairy commodity powders
(NFDM, buttermilk powder, whey powder, whey protein) are `Dairy`; purified
single dairy-derived compounds sold as isolated manufacturing inputs
(lactose powder, sodium caseinate) are `Food Additives/Ingredients`.
**Dairy-based coffee creamer** (cream-, milk-, or half-and-half-based,
including flavored varieties) is `Dairy`. Milk- or goat-milk-based infant
formula moves to `Baby/Toddler Food`, not `Dairy`.

**Eggs** — Eggs and egg products where the egg *is* the product: shell
eggs of any grade, size, color, or pack; pasteurized shell eggs; hard-
cooked/hard-boiled/peeled eggs including seasoned packs; liquid, frozen,
and dried egg (whole, white, yolk); preserved, salted, century, and
pickled eggs of any bird (chicken, duck, quail); egg salad sold as egg
salad; RTE items where egg is the overwhelming component (egg bites, plain
omelets, scrambled-egg trays).

**Beef/Pork/Poultry/Game Meats** — All meat products where the meat is the
product: cuts, ground meat, jerky, deli meats (bologna, capicola,
pepperoni, ham), sausage. Game meats (venison, elk, bison, kangaroo,
rabbit) belong here. Excludes eggs (separate label), meat-*named*
seasonings/rubs/marinades/injections/gravy mixes, buns, sandwiches, broth,
and plant-based analogs — see boundary rules.

**Seafood** — Fish and shellfish, fresh, frozen, smoked, canned, or cured.
Includes battered/breaded fish portions, ceviche, poke kits, sushi rolls,
roe, eel, protein-dominant seafood salads (tuna salad). Excludes seafood-
named seasonings and cures (→ `Spices/Condiments`).

**Produce** — Fresh, frozen, dried, or minimally processed fruits and
vegetables. Includes fresh-cut kits, slaws and coleslaw, pico de gallo,
mirepoix, guacamole, salad greens, fresh herbs (dried herbs and spices →
`Spices/Condiments`), cactus/nopales, mushrooms, seaweed, all dried fruit
(raisins, apricots, dates, prunes, figs, plums), whole and pickled olives,
pickles, turnip pickles. Packing medium never governs — produce packed in
oil (peppers in oil, olives & feta in olive oil) is still `Produce`, not
`Oils/Fats`. Vegetable-dominant lightly-dressed salads (coleslaw, cucumber
salad) are `Produce`; potato salad moves to `Prepared/Frozen` (see boundary
rules).

**Plant Protein** — Beans and legumes in all forms, including cooked bean
dishes (baked beans, refried beans, calico beans, chili beans); soy
protein isolates and concentrates, textured vegetable protein, tofu, bean
curd, edamame, lentils, chickpeas; hummus and other legume-based dips and
spreads; falafel; veggie/black-bean burgers; **plant-based meat, egg,
cheese, and yogurt analogs** (Impossible, Just Egg, vegan cheese,
dairy-free pudding) classified by composition, not by what they imitate;
**plant milks** (oat, almond, soy, rice, cashew, coconut-milk beverages
sold and consumed as the primary beverage/food); and **plant-protein-based
protein powders and RTD shakes** (pea, soy, rice, hemp isolate — scoop-
format or ready-to-drink, marketed as a supplement or not). **Plant-based
coffee creamer is explicitly excluded from this label** — see `Beverages`.
The unifying test: the product's identity must be defined by a plant
protein or plant-milk base *as the primary food*, not as an additive
fraction of another product.

**Grains/Cereal** — Dry pasta, noodles, rice, flour, semolina, farina,
masa, tapioca, breakfast cereal, oatmeal, cornmeal. Also bulk industrial
batter, predust, breader, and cracker-meal blends sold in 20–2,000 lb
quantities — these belong here, not `Uncategorized`, even when the
description is just a code plus "BATTER MIX X1, 50 LBS."

**Bakery** — Finished baked goods: bread, rolls, buns, tortillas,
pastries, danishes, cookies, cakes, doughnuts, pie shells, croutons,
biscotti, baklava, jalebi. Also raw dough and mixes intended to produce a
specific baked good (scone mix, hushpuppy mix, crepe mix, pizza dough,
beer bread mix, wine brownie mix). Absorbs hamburger/hot-dog buns that
keyword rules mismatched to meat labels.

**Prepared/Frozen** — Composite ready-to-eat or heat-and-eat meals where
no single component dominates: sandwiches, subs, hoagies, wraps, paninis,
pinwheels, boxed lunches, quiche, calzones, pierogi, entrées, meal bowls,
breakfast scrambles, frozen waffles and French toast, tamales, hot dogs as
assembled items, soups, water-based frozen novelties (Italian ice,
popsicles, bolis), non-dairy frozen desserts. Also **ready-to-use liquid
broth, stock, and bone broth** (poured and consumed or cooked with at
strength — see broth boundary below) and **dressed grain/pasta salads and
potato salads** (macaroni salad, potato salad, orzo/quinoa/couscous salad).
Composite breakfast items with egg present but not dominant (sausage &
egg on a bun) stay here, not `Eggs`.

**Snacks/Candy** — Chips, pretzels, crackers, popcorn, snack mixes, candy,
chocolate, gum, meltaways, nutrition and protein bars, cookies sold as
snack items, chicharrones, confectionery coating.

**Nuts/Seeds** — Nuts, seeds, nut butters, peanut products, and all trail
mixes and sweet-and-salty snack mixes built on a nut or dried-fruit base.
Seeds sold for sprouting (alfalfa, clover). Honey-roasted nuts stay here
(honey as an ingredient never governs).

**Beverages** — Soda, juice, water, coffee, tea, drink mixes, coffee pods,
alcoholic beverages (beer, wine, cider, spirits, hard seltzer, RTD
cocktails), non-alcoholic cocktail mixers and drink syrups/concentrates.
**Coffee creamer is `Beverages` by default** — liquid or powdered,
dairy-free or plant-based (oat, soy, almond, cashew), synthetic non-dairy
(oils, starches, sodium caseinate/casein derivatives). Only **dairy-based**
creamer carves out to `Dairy`; plant-based creamer stays here, unlike
plant milk itself (a plant creamer is compositionally an oil/thickener
additive product, not a protein-bearing plant-milk food — see revision
history). Creamer *stabilizer and emulsifier systems* sold in bulk for
manufacturing (e.g. "Grindsted Creamer 2103 Stabilizer System, 50 lb bag")
are `Food Additives/Ingredients`, not `Beverages` — they contain no
creamer.

**Spices/Condiments** — Spices, seasoning blends, rubs, chile powders and
pastes (fresh whole peppers stay `Produce`), sauces, marinades, dressings
and vinaigrettes (even at 60%+ oil — the oil is not the product), salsa
(jarred), jams and jellies, tapenade, miso, vinegar, salt, extracts,
food-grade colorants sold as seasoning, carob powder, dried herbs and
spices. Also **honey** (pure, raw, comb, creamed/whipped/spun, flavored),
**liquid/viscous sweeteners** (molasses, agave nectar, maple syrup, cane
and coconut syrups, table syrups, consumer stevia/monk-fruit), **meat-named
seasonings/rubs/marinades/injections/gravy mixes** (the animal in the name
is not a meat signal), and **concentrated broth bases, bouillon
cubes/granules/powders, and soup bases** (dosed by the teaspoon as
flavoring, vs. ready-to-use broth which is `Prepared/Frozen` — see
boundary rules). Vegetable/sauce dips (salsa, ranch, French onion,
spinach-artichoke) belong here, not `Produce` or `Plant Protein`.

**Oils/Fats** — Cooking, frying, and salad oils; olive oil; liquid and
solid shortening; lard, tallow, ghee; margarine and vegetable-oil butter
substitutes; culinary infused oils where the oil is what you buy and use
(garlic oil, chili oil sold as oil). The oil must be the product, not the
medium and not an ingredient — see the detailed boundary rules below.

**Supplements** — Vitamins, minerals, capsules, tablets, softgels,
digestive enzymes, probiotics, colostrum, herbal extracts, weight-loss
drops, energy gels, pre-workout, medical foods and enteral/oral
nutritional formulas sold to consumers, dysphagia-thickened beverages
(honey-consistency thickened drinks), claim-bearing honey sachets
(performance/therapeutic/sexual-enhancement claims, or honey blended with
a botanical/functional extract), kratom, oil in a supplement dosage form
(hemp oil gummies), a sweetener in a supplement dosage form from a
supplement brand (herbal tincture stevia). **Protein powders and RTD
shakes stay here only when the protein source is animal-derived or
blended/non-plant** (whey, casein, collagen, egg-white protein, or a
whey/plant blend where plant isn't the sole or dominant source) —
plant-only-sourced protein powders and shakes go to `Plant Protein`
instead (see above; this reverses the API proposal's blanket
`Supplements` call for protein powders).

**Baking Supplies** — Inputs and decorations for baking, as opposed to
finished baked goods. Plain granulated/brown/cane/powdered/sanding sugar,
sprinkles, nonpareils, food coloring and airbrush color, luster and jewel
dust, icing and frosting mixes, fondant, gum paste and pastillage,
confectionery coating and discs, baking powder, baking soda, yeast. Test
for the dry-sugar vs. liquid-sweetener boundary: dry crystalline sugar you
bake with → `Baking Supplies`; liquid or viscous sweetener you pour or
spread → `Spices/Condiments`.

**Food Additives/Ingredients** — Industrial and manufacturing inputs sold
in bulk: stabilizer and emulsifier systems (including creamer stabilizer
systems), dough conditioners, food starches, carrageenan, citrate salts,
calcium sulfate and chloride, phosphoric acid, L-cysteine, yeast extract,
lactose powder, sodium caseinate as an isolated ingredient, bulk enzymes
(pepsin), food-grade limestone, nitrite curing blends (functional, not
flavoring), purified sweetener compounds sold in bulk to manufacturers
(Reb M, erythritol, sorbitol, sucralose, allulose in drums/totes), bulk
blended ingredient mixes (e.g. "MILK-N-EGG MIX" sold in 50 lb bags), oil
as one component of a manufacturing input (encapsulated sugar with
hydrogenated palm oil).

**Non-Food Item** — Not intended for human consumption: cookware, pots,
knives, utensils, plates, cups, serving trays, bakeware, cosmetics, hair
products, tooth powder, oral-care and cosmetic kits, decorative pigments.
**Pet food and treats are explicitly excluded** — see `Pet Food/Treats`.

**Baby/Toddler Food** — Infant and toddler purees, pouches, and jarred
baby food; infant cereal; teething and toddler snacks explicitly marketed
for infants/toddlers; **and all infant and toddler formula, regardless of
protein base** (milk-based, soy-based, amino-acid-based, goat-milk-based —
formula is one product family and stays together rather than fragmenting
by protein source). Adult medical/enteral nutrition is not baby food →
`Supplements`. A cracker or puff sold to the general market is
`Snacks/Candy` even if toddlers eat it — the label must be
infant/toddler-directed.

**Pet Food/Treats** — Food, treats, chews, and dietary supplements
manufactured and sold for animal (not human) consumption: dog food, cat
food, pet treats, pet chews, pet vitamins. Distinct from `Non-Food Item`
because it is genuinely food — subject to the same class of recall hazards
(*Salmonella*, foreign material, nutritional deficiency) as any other food
label, just not for people.

**Uncategorized** — Bare SKUs and product codes with no food-identifying
text; unlabeled bulk shipments; gift baskets and assortments; "multiple
products" entries; anything genuinely ambiguous.

---

## 4. Boundary rules

| Boundary | Rule |
|---|---|
| **Bakery vs. Baking Supplies** | Bakery = finished goods you eat. Baking Supplies = inputs and decorations. A frosting mix is Baking Supplies; a frosted cake is Bakery. |
| **Baking Supplies vs. Food Additives** | Consumer-facing baking goods vs. industrial manufacturing inputs. Sugar and sprinkles are Baking Supplies; a 2,000 lb tote of emulsifier system is Food Additives. |
| **Ingredient vs. product** | An ingredient named in a finished product does not determine the category. Brown-sugar oatmeal is `Grains/Cereal`; mozzarella sticks are `Prepared/Frozen`; ricotta gnocchi is `Grains/Cereal`. |
| **Protein vs. Prepared/Frozen** | If a single named protein dominates, use the protein category (beer-battered cod → `Seafood`). If it's a composite meal or sandwich, use `Prepared/Frozen` (Italian sub → `Prepared/Frozen`). |
| **Cooked beans** | Cooked bean dishes are `Plant Protein`, not `Prepared/Frozen`. This overrides the composite-meal rule. |
| **Supplements vs. Food Additives** | Consumer dosage forms are Supplements. The same substance in 25–50 kg drums for manufacturing is Food Additives (bulk pepsin, bulk magnesium citrate). |
| **Frozen novelties** | Dairy-based (ice cream, sherbet, gelato) → `Dairy`. Water-based (Italian ice, popsicles, bolis) and non-dairy frozen desserts → `Prepared/Frozen`. |
| **Snack mixes** | Nut- or dried-fruit-based → `Nuts/Seeds`. Chip-, cracker-, or corn-based → `Snacks/Candy`. |
| **Chile products** | Fresh whole peppers → `Produce`. Powders, pastes, roasted/diced processed chile, and chile kits → `Spices/Condiments`. |
| **Batter mixes** | Bulk industrial batter/predust/breader → `Grains/Cereal`, not `Uncategorized`. |
| **Eggs vs. meat** | The meat label covers flesh only. "Chicken" signals meat for breast/thigh/wing/tender/patty/sausage; it signals `Eggs` for egg/shell egg/hard-cooked. Chicken egg → `Eggs`. Chicken breast → meat. |
| **Egg nog** | → `Dairy`, not `Eggs` — overwhelmingly a milk-and-cream product. |
| **Composite breakfast items** | Egg present but not dominant (sausage & egg on a bun) → `Prepared/Frozen`, not `Eggs`. |
| **Oils/Fats vs. everything else** | The oil must be the product, not the medium and not an ingredient. Food packed *in* oil → the food's own label (peppers in oil → `Produce`). Dressings/vinaigrettes/mayo/aioli/pesto/marinades → `Spices/Condiments` even at 60%+ oil. Butter is `Dairy`; margarine is `Oils/Fats`. Oil in a supplement dosage form → `Supplements`. Oil as one component of a manufacturing input → `Food Additives/Ingredients`. Oil named in a finished snack → the snack's own label. |
| **Broth/stock/bouillon** | Ready-to-use liquid broth/stock/bone broth (poured/cooked at strength) → `Prepared/Frozen`. Concentrated bases, bouillon cubes/granules/powders, soup bases (dosed by the teaspoon) → `Spices/Condiments`. The animal in the name does not make it meat — chicken broth is not `Beef/Pork/Poultry/Game Meats`. |
| **Honey as ingredient** | Never governs — honey-roasted peanuts → `Nuts/Seeds`; honey wheat bread → `Bakery`; honey mustard dressing → `Spices/Condiments`. |
| **Alcohol as ingredient** | Never changes the category — rum raisin ice cream → `Dairy`; beer bread mix → `Bakery`; port wine cheese → `Dairy`; beer-battered cod → `Seafood`; vodka sauce → `Spices/Condiments`. |
| **Dressed deli salads** | Grain/pasta-based and potato-based → `Prepared/Frozen`. Protein-dominant → the protein label (tuna salad → `Seafood`, egg salad → `Eggs`). Vegetable-dominant, lightly dressed → `Produce`. |
| **Hummus and dips** | Legume-based (hummus, black bean dip, edamame dip) → `Plant Protein`. Cheese/cream-cheese-based → `Dairy`. Vegetable/sauce-based (salsa, ranch, tapenade) → `Spices/Condiments`. |
| **Coffee creamer** | Dairy-based → `Dairy`. Plant-based and synthetic non-dairy → `Beverages` (does not follow plant milk into `Plant Protein` — see revision history). Creamer stabilizer/emulsifier systems → `Food Additives/Ingredients`. |
| **Plant analogs** | Classify by composition, not by what they imitate. Meat/egg/cheese/yogurt analogs and plant milk → `Plant Protein`. Non-dairy frozen desserts → `Prepared/Frozen` (accepted cost: an ice cream and its vegan twin land in different labels). |
| **Protein powders/RTD shakes** | Plant-only-sourced (pea, soy, rice, hemp) → `Plant Protein`. Animal-derived or blended/non-plant (whey, casein, collagen) → `Supplements`. |
| **Medical/enteral nutrition** | Medical foods, oral nutritional supplements, enteral formulas, dysphagia-thickened beverages → `Supplements`, regardless of how a keyword pass scattered the same product family. |
| **Formula** | All infant/toddler formula, regardless of protein base → `Baby/Toddler Food`. Adult medical/enteral nutrition stays `Supplements`. |
| **Non-food inside food records** | Cookware, tableware, drinkware, cosmetic/oral-care kits → `Non-Food Item`. Pet food/treats → `Pet Food/Treats`, not `Non-Food Item`. |

---

## 5. Coverage-hole rules

**Alcohol** → `Beverages` (beer, wine, cider, spirits, hard seltzer, RTD
cocktails). Non-alcoholic cocktail mixers, drink syrups, and drink
concentrates → `Beverages` regardless of bottle size. Table syrup,
pancake syrup, and dessert sauces stay `Spices/Condiments`.

**Coffee creamer** → see the Beverages/Dairy rules above (two-way split:
dairy → `Dairy`, everything else → `Beverages`).

**Broth/stock/bouillon** → see the broth boundary rule above (split by
concentration: ready-to-use → `Prepared/Frozen`; concentrated/bouillon →
`Spices/Condiments`).

**Baby food (non-formula purees)** → `Baby/Toddler Food` (new label — see
category rule above; prevents fragmenting one product line by ingredient).

**Honey** → `Spices/Condiments`, with a hard carve-out: honey in
single-serve sachets carrying performance, energy, or therapeutic claims,
or blended with a botanical/functional extract → `Supplements`.

**Agave/stevia/molasses** → `Spices/Condiments` (nutritive sweeteners
sold as sweeteners), with two exceptions: dry crystalline baking sugars →
`Baking Supplies`; purified sweetener compounds sold in bulk to
manufacturers → `Food Additives/Ingredients`. A sweetener in a supplement
dosage form from a supplement brand follows the dosage form →
`Supplements`.

---

## 6. Known gaps

1. **Raw single-ingredient meat cuts are largely untested.** FDA recall
   records under-represent raw primal cuts (USDA-jurisdiction territory).
   The merged meat label is validated against deli meat, cured meat,
   jerky, and cooked cuts, not raw whole cuts.
2. **`Baking Supplies` has thin direct evidence.** It was not among the
   design sample's exhaustive, coverage-hole, or stratified draws; its
   boundaries were inferred from adjacent rows. Along with
   `Food Additives/Ingredients`, it is one of the least-evidenced labels
   in the set — worth a dedicated sample if a future validation pass
   is run.
3. **The full-dataset relabel is a clean break, not a mapping.** Old
   keyword labels are not mapped forward — the design-sample review found
   systematic, non-mappable keyword errors (e.g. `Beef → Bakery` for bun
   rows is correct, `Beef → Beef` for actual beef rows is also correct;
   no single mapping function resolves both). The legacy label is
   retained in a separate column for diff-based QA only, never fed to the
   classifier.

---

## 7. Revision history

- **v1** (API proposal, Claude Opus 5 against the ~5,000-row design
  sample): 20 labels — the log's 18 plus `Eggs` and `Baby/Toddler Food`.
  Routed plant milk and plant-based coffee creamer to `Beverages`, all
  protein powders to `Supplements`, and pet food to `Non-Food Item`.
- **v2** (Mai's four corrections, applied as a manual re-grouping of the
  same cited evidence — no new API call): plant-protein-based protein
  powders/shakes moved to `Plant Protein`; plant milk moved to
  `Plant Protein`; pet food split into a new `Pet Food/Treats` label;
  coffee creamer split by base (dairy → `Dairy`, plant-based → tentatively
  `Plant Protein`). Label count: 21.
- **v2 correction** (this document): plant-based coffee creamer reverted
  from `Plant Protein` back to `Beverages`. Rationale: v1's cited
  creamer evidence was entirely brand-name examples, never ingredient or
  protein content. Real plant-based coffee creamer is compositionally an
  oil/thickener/sugar additive product with near-zero protein — unlike
  plant milk itself, which is sold and consumed as the primary
  protein-bearing beverage/food. Plant milk keeps its `Plant Protein`
  placement; coffee creamer is a two-way split (dairy → `Dairy`,
  everything else including plant-based → `Beverages`), not three-way.
  Label count unchanged at 21.
