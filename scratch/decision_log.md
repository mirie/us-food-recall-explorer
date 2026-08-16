# Food Recall Classification — Decision Summary

Rules settled on while classifying the 3,554-row `Uncategorized` subset. Intended as source material for a full-dataset classification prompt.

**Read the "Known gaps" section before using this.** These rules were derived from a pre-filtered slice and do not cover several categories that will appear in volume in the full dataset.

---

## 1. Label set (18)

```
Dairy
Nuts/Seeds
Beverages
Supplements
Seafood
Bakery
Prepared/Frozen
Grains/Cereal
Snacks/Candy
Plant Protein
Produce
Spices/Condiments
Oils/Fats
Beef/Pork/Poultry/Game Meats
Baking Supplies
Food Additives/Ingredients
Non-Food Item
Uncategorized
```

Changed from the original scheme: `Beef`, `Pork`, and `Poultry/Eggs` were merged into `Beef/Pork/Poultry/Game Meats`; `Baking Supplies`, `Food Additives/Ingredients`, and `Non-Food Item` were added.

---

## 2. Governing principle

> Classify what the product **most fundamentally is**, not every ingredient it contains.

An ice cream product containing nuts is `Dairy`, not `Nuts/Seeds`. A cheddar party mix is `Snacks/Candy`, not `Dairy`. When a description names both a base food and a preparation, the base food usually wins unless the preparation transforms it into a different kind of product.

When nothing in the description reliably indicates a category, use `Uncategorized` rather than guessing.

---

## 3. Category rules

**Produce** — Fresh, frozen, dried, or minimally processed fruits and vegetables. Includes fresh-cut kits, slaws and coleslaw, pico de gallo, mirepoix, guacamole, salad greens, herbs, cactus/nopales, mushrooms, seaweed. Includes **all dried fruit** (raisins, apricots, dates, prunes, figs, plums). Includes whole and pickled olives, pickles, and turnip pickles sold as food.

**Plant Protein** — Beans and legumes in all forms: dry, canned, and **cooked bean dishes** (baked beans, refried beans, calico beans, chili beans). Also soy protein isolates and concentrates, textured vegetable protein, tofu, bean curd, edamame, lentils, chickpeas, hummus, falafel, veggie/black-bean burgers, plant protein powders.

**Dairy** — Milk, cheese of all kinds, cream, butter, yogurt, ice cream, sherbet, gelato, frozen custard, half-and-half, paneer, quark, mascarpone. **Milk- or goat-milk-based infant formula is Dairy**; soy- or amino-acid-based formula is `Plant Protein`.

**Beef/Pork/Poultry/Game Meats** — All meat products where the meat is the product: cuts, ground meat, jerky, deli meats (bologna, capicola, pepperoni, ham), sausage. **Game meats** (venison, elk, bison, kangaroo, rabbit) belong here.

**Seafood** — Fish and shellfish, fresh, frozen, smoked, canned, or cured. Includes battered/breaded fish portions, ceviche, poke kits, sushi rolls, roe, eel.

**Grains/Cereal** — Dry pasta, noodles, rice, flour, semolina, farina, masa, tapioca, breakfast cereal, oatmeal, cornmeal. Also **bulk industrial batter, predust, breader, and cracker-meal blends** sold in 20–2,000 lb quantities.

**Bakery** — Finished baked goods: bread, rolls, buns, tortillas, pastries, danishes, cookies, cakes, doughnuts, pie shells, croutons, biscotti, baklava, jalebi. Also raw dough and mixes intended to produce a specific baked good (scone mix, hushpuppy mix, crepe mix, pizza dough).

**Prepared/Frozen** — Composite ready-to-eat or heat-and-eat meals where no single component dominates: sandwiches, subs, paninis, wraps, burritos, quiche, calzones, pierogi, entrées, meal bowls, breakfast scrambles, frozen waffles and French toast, tamales, hot dogs as assembled items, soups, water-based frozen novelties (Italian ice, popsicles, bolis).

**Snacks/Candy** — Chips, pretzels, crackers, popcorn, snack mixes, candy, chocolate, gum, meltaways, nutrition and protein bars, cookies sold as snack items, chicharrones, confectionery coating.

**Nuts/Seeds** — Nuts, seeds, nut butters, peanut products, and **all trail mixes and sweet-and-salty snack mixes built on a nut or dried-fruit base**. Also seeds sold for sprouting (alfalfa, clover).

**Beverages** — Soda, juice, water, coffee, tea, drink mixes, coffee pods, shelf-stable and refrigerated drinks.

**Spices/Condiments** — Spices, seasoning blends, rubs, chile powders and pastes, whole and processed chile products, sauces, marinades, dressings, salsa (jarred), jams and jellies, tapenade, miso, vinegar, salt, extracts, food-grade colorants sold as seasoning, carob powder.

**Oils/Fats** — Cooking oils, olive oil, shortening, lard, ghee, margarine, butter substitutes. *(No precedent set — see gaps.)*

**Supplements** — Vitamins, minerals, capsules, tablets, softgels, powders, digestive enzymes, probiotics, colostrum, herbal extracts, protein and meal-replacement shakes, weight-loss drops, energy gels, pre-workout, medical foods sold to consumers.

**Baking Supplies** — Inputs and decorations for baking, as opposed to finished baked goods. Plain granulated/brown/cane sugar, sanding sugar, sprinkles, nonpareils, food coloring and airbrush color, luster and jewel dust, icing and frosting mixes, fondant, gum paste and pastillage, confectionery coating and discs, baking powder, baking soda, yeast.

**Food Additives/Ingredients** — Industrial and manufacturing inputs sold in bulk: stabilizer and emulsifier systems, dough conditioners, food starches, carrageenan, citrate salts, calcium sulfate and chloride, phosphoric acid, L-cysteine, yeast extract, lactose powder, bulk enzymes (pepsin), food-grade limestone.

**Non-Food Item** — Not intended for consumption: cookware, pots, knives, utensils, plates, cups, serving trays, bakeware, cosmetics, hair products, tooth powder, pet food, decorative pigments.

**Uncategorized** — Bare SKUs and product codes with no food-identifying text; unlabeled bulk shipments; gift baskets and assortments; "multiple products" entries; anything genuinely ambiguous.

---

## 4. Boundary rules

These are the distinctions that caused the most trouble. Each resolves a specific recurring collision.

| Boundary | Rule |
|---|---|
| **Bakery vs. Baking Supplies** | Bakery = finished goods you eat. Baking Supplies = inputs and decorations. A *frosting mix* is Baking Supplies; a *frosted cake* is Bakery. |
| **Baking Supplies vs. Food Additives** | Consumer-facing baking goods vs. industrial manufacturing inputs. Sugar and sprinkles are Baking Supplies; a 2,000 lb tote of emulsifier system is Food Additives. |
| **Ingredient vs. product** | An ingredient named in a finished product does not determine the category. Brown-sugar oatmeal is `Grains/Cereal`; mozzarella sticks are `Prepared/Frozen`; ricotta gnocchi is `Grains/Cereal`. |
| **Protein vs. Prepared/Frozen** | If a single named protein dominates, use the protein category (beer-battered cod → `Seafood`). If it's a composite meal or sandwich, use `Prepared/Frozen` (Italian sub → `Prepared/Frozen`). |
| **Cooked beans** | Cooked bean *dishes* are `Plant Protein`, not `Prepared/Frozen`. This overrides the composite-meal rule. |
| **Supplements vs. Food Additives** | Consumer dosage forms are Supplements. The same substance in 25–50 kg drums for manufacturing is Food Additives (bulk pepsin, bulk magnesium citrate). |
| **Frozen novelties** | Dairy-based (ice cream, sherbet, gelato) → `Dairy`. Water-based (Italian ice, popsicles, bolis) → `Prepared/Frozen`. |
| **Snack mixes** | Nut- or dried-fruit-based → `Nuts/Seeds`. Chip-, cracker-, or corn-based → `Snacks/Candy`. |
| **Chile products** | Fresh whole peppers → `Produce`. Powders, pastes, roasted/diced processed chile, and chile kits → `Spices/Condiments`. |
| **Batter mixes** | Bulk industrial batter/predust/breader → `Grains/Cereal`, not `Uncategorized`, even when the description is just a code plus "BATTER MIX X1, 50 LBS". |

---

## 5. Known gaps — read before running

These rules came from the `Uncategorized` remainder of a keyword-rule pass, meaning the keyword rules had already removed the easy, obvious cases. The subset is therefore **skewed toward hard and unusual products** and contains almost none of the high-volume ordinary ones.

Specifically, in 3,554 rows the subset contained **zero egg products, zero oil/fat products, and one poultry row.** All of these will appear in volume in the full dataset, and no precedent exists for them here.

**Unresolved — needs a decision before the run:**

1. **Eggs have no home.** Merging `Poultry/Eggs` into `Beef/Pork/Poultry/Game Meats` removed the only label naming eggs, and the merged label reads as a meat category. Shell eggs and liquid eggs are a large, recurring recall category (salmonella). Either add `Eggs`, restore `Poultry/Eggs` alongside the meat label, or state explicitly that eggs go in the merged meat category despite the name.

2. **Plain milk, plain produce, plain meat cuts.** No examples in the subset. The rules above should handle them, but they were never tested against real descriptions.

3. **Oils/Fats is untested.** No examples appeared, so the boundary against `Spices/Condiments` (infused oils, oil-based dressings) was never exercised.

4. **Taxonomy reconciliation.** The ~25,607 rows labeled by the keyword rules still use the original scheme, including a standalone `Beef` category that no longer exists. A full-dataset run should either relabel everything under the new taxonomy or map the old labels forward explicitly.

5. **These rules have not been validated against keyword-assigned labels.** No existing label was reviewed. If the keyword rules encode conventions that conflict with the rules above, that conflict is currently invisible.
