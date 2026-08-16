# Final Food-Recall Classification Taxonomy — v2

---

## Final label set

**20 labels** (the log's 18, plus `Eggs` and `Baby/Toddler Food`).

| # | Label | What changed vs. the log's 18 |
|---|---|---|
| 1 | **Dairy** | *Changed* — explicitly absorbs flavored milk, egg nog, cheese-based dips/spreads, and bulk dairy commodity powders (NFDM, whey, buttermilk powder); loses infant formula to `Baby/Toddler Food`. |
| 2 | **Eggs** | **New** — the sample contains 60+ pure egg-product rows with no home in the 18. |
| 3 | **Beef/Pork/Poultry/Game Meats** | *Changed in scope, not name* — now unambiguously excludes eggs (a separate label exists); explicitly excludes meat-*named* seasonings, buns, sandwiches, broths, and plant analogs. |
| 4 | **Seafood** | *Clarified* — protein-dominant seafood salads in; seafood-named seasonings and cures out. |
| 5 | **Produce** | *Clarified* — fresh herbs in (dried herbs → Spices); packing medium never governs (peppers/olives *in oil* are Produce, not Oils/Fats). |
| 6 | **Plant Protein** | *Changed* — gains vegan meat/egg/cheese analogs; loses consumer protein powders and RTD shakes to `Supplements`. |
| 7 | **Grains/Cereal** | Unchanged. |
| 8 | **Bakery** | Unchanged (absorbs the large block of hamburger/hot-dog buns the keyword pass mislabeled `Beef`). |
| 9 | **Prepared/Frozen** | *Changed* — gains ready-to-use liquid broth/stock/bone broth, dressed pasta/potato deli salads, and non-dairy frozen desserts. |
| 10 | **Snacks/Candy** | Unchanged. |
| 11 | **Nuts/Seeds** | Unchanged. |
| 12 | **Beverages** | *Changed* — gains alcoholic beverages, all coffee creamers (dairy and non-dairy), plant milks, and cocktail mixers / drink syrups / drink concentrates. |
| 13 | **Spices/Condiments** | *Changed* — gains honey and all liquid/viscous sweeteners, meat-named rubs/marinades/injections/gravy mixes, and bouillon / soup bases / concentrated broth bases. |
| 14 | **Oils/Fats** | *Confirmed and bounded* — rule survives contact with 40+ real rows; boundary added against packing medium, dressings, and butter. |
| 15 | **Supplements** | *Changed* — gains medical foods, enteral/oral nutritional formulas, dysphagia-thickened beverages, all protein powders and RTD protein shakes, claim-bearing honey sachets, and kratom. |
| 16 | **Baking Supplies** | Unchanged (with a new dry-sugar vs. liquid-sweetener test). |
| 17 | **Food Additives/Ingredients** | *Changed* — gains creamer stabilizer/emulsifier systems, nitrite curing blends, and purified sweetener compounds sold in bulk. |
| 18 | **Non-Food Item** | *Changed* — explicitly names pet food/treats and oral-care/cosmetic kits, both of which appear inside these food-recall records. |
| 19 | **Baby/Toddler Food** | **New** — consolidates infant/toddler purees, pouches, cereals, and *all* infant formula regardless of protein base. |
| 20 | **Uncategorized** | Unchanged. |

---

## Open question resolutions

### Q1 — Eggs: add the label

**Resolution: add `Eggs`. It is not optional.**

**Evidence.** The `exhaustive:Poultry/Eggs` block is not mostly poultry meat — a very large share of it is egg product with no defensible home in the 18:

- **Shell eggs** (the single densest cluster): Abbotsford/Papetti's/Glenview/Crystal Farms pasteurized shell eggs (F-0023-2015), Good Earth Egg Company (F-0147-2017), Gravel Ridge Farms (F-0028-2019), Milo's Poultry Farms / Happy Quackers duck eggs (F-1837-2024), Kirkland Organic Pasture-Raised (F-0314-2025), and long Eggland's Best / Vital Farms / Pete & Gerry's / Market Pantry / Simply Balanced retail runs (F-1621- through F-1626-2019, F-1762- through F-1764-2019, F-1825-2019, F-1259-2020, H-0210-2025, H-0171-2026, H-0170-2026, H-0153-2026, H-0011-2026, H-0399-2025).
- **Hard-cooked eggs**: the entire Almark Foods 2020 *Listeria* recall (F-0611-2020 through F-0629-2020, plus F-0602-2020 bulk broken egg whites).
- **Further-processed egg**: Papetti's refrigerated scrambled egg (F-0061-2015), Deb-El dried whole eggs (F-1608-2014, F-1947-2014), Grand Prairie scrambled (F-1006-2019).
- **Preserved/specialty eggs**: Yangsheng preserved duck eggs (F-0884-2013), cooked salted duck eggs (F-0863-2013), Taiwan preserved egg (F-2021-2015), Oma's Choice pickled quail eggs (F-0726-2014).
- **Egg-forward RTE**: Organic Valley egg bites (F-1363-2020), chile verde egg bites (F-0746-2025), Ossie's egg with scallion (F-0253-2017).

Filing all of this under a label literally named "…Meats" is wrong on its face, and splitting it across `Dairy` (hard-cooked eggs?) and `Prepared/Frozen` (egg bites?) would fragment one coherent recall population that has its own hazard signature (*Salmonella* Enteritidis, *Listeria* in hard-cooked lines).

**Rule — Eggs.**
> Eggs and egg products where the egg *is* the product: shell eggs of any grade, size, color, or pack (cartons, flats, 15-dozen foodservice cases, loose bulk); pasteurized shell eggs; hard-cooked / hard-boiled / peeled eggs, including salt-and-pepper and seasoned packs; liquid, frozen, and dried egg (whole, white, yolk); preserved, salted, century, and pickled eggs of any bird (chicken, duck, quail); egg salad sold as egg salad; and RTE items in which egg is the overwhelming component (egg bites, plain omelets, scrambled-egg trays).

**Boundary — Eggs vs. Beef/Pork/Poultry/Game Meats.**
> The meat label covers the **flesh** of birds and mammals only. "Chicken" in a product name is a meat signal for *breast, thigh, wing, tender, patty, sausage*; it is an egg signal for *egg, shell egg, hard-cooked*. Chicken egg → `Eggs`. Chicken breast → meat. Duck egg → `Eggs`. Duck breast → meat.

**Three further boundaries the sample forces:**
- **Egg nog → `Dairy`, not `Eggs`.** F-1477-2015 (Snoqualmie) and F-0562-2018 (365 / Harrisburg Dairies) are Grade A dairy-plant products that are overwhelmingly milk and cream. The word "egg" in the name is not the product.
- **Composite breakfast items → `Prepared/Frozen`.** "Sausage & Egg (on bun)" (F-0851-2015), "Cheesy Eggs w/Link Sausage & Dinner Roll" (F-0837-2015), "Wakefield Chorizo & Egg on Ciabatta" (F-1404-2024), Healthy Choice Pesto & Egg White bowls (F-0982-2020). Egg present ≠ egg dominant.
- **Bulk blended egg ingredient → `Food Additives/Ingredients`.** "MILK-N-EGG MIX, NET WEIGHT: 50 LBS, processed from nonfat dried milk, dried whey, dried egg whites" (H-0693-2026) is a manufacturing input, not an egg product.

Also note two egg-adjacent traps the sample contains: **Gasco "Golden Egg Yellow Shade" liquid food color** (F-1808-2013, F-1152-2019) contains no egg and is `Baking Supplies`; **"Porfirio's Egg Fettucine"** (F-0185-2017) is `Grains/Cereal`.

---

### Q2 — Plain milk, plain produce, plain meat cuts: rules mostly hold; three adjustments

**Plain milk — rules hold, with two additions.** The stratified Dairy sample contains straightforward fluid milk (Wawa whole milk, Fairway 1%, Natural by Nature 1%, Clover Valley 2%, Lactaid skim, Organic Valley UHT). These classify cleanly as `Dairy`. Two things the log did not anticipate:

1. **Flavored milk is Dairy, not Beverages.** Prairie Farms 1% Lowfat Chocolate Milk (F-0160-2021), Farmer's All Natural 2% Chocolate Milk (F-1745-2022), Wawa Double Dutch Chocolate Milk (H-0586-2026), Wawa Strawberry Milk (H-0044-2026), Clover Valley 1% Chocolate (H-0400-2025). The keyword pass scattered these into `Snacks/Candy` and `Produce`. Add an explicit line.
2. **Bulk dairy commodity powders stay Dairy; formulated dairy *systems* are Food Additives.** The sample has Low Heat NFDM in 50 lb bags and 2,200 lb totes (F-1981-2017, H-0698-2026), Sweet Cream Buttermilk Powder 50# (F-1190-2017), Liquid Whey bulk (F-1898-2017), Grande Bravo 300 whey protein 50 lb (F-1363-2024). These are the dairy commodity itself → `Dairy`. But "Grindsted Creamer 2103 Stabilizer and Emulsifier System, 50 lb bag" (F-1316-2024, and 2160/2395/1817) contains no dairy and is a hydrocolloid system → `Food Additives/Ingredients`. **This supersedes the log's "lactose powder → Food Additives" line only in part:** purified single compounds (lactose, sodium caseinate as an isolated ingredient) remain `Food Additives`; dried whole-commodity milk fractions remain `Dairy`.

**Plain produce — rules hold, with one addition.** Whole cantaloupe (F-0617-2024), cucumbers (F-0313-2025, H-0217-2025), brussels sprouts (F-0414-2023), romaine (F-1429-2023), bulk onions (F-1273-2020), peaches (F-1438-2020), enoki mushrooms (F-0890-2020, H-0898-2026) all classify cleanly. Addition: **fresh herbs are Produce; dried herbs and spices are Spices/Condiments.** The sample contains both — bunched Italian parsley and Hawaii Fresh Sweet Basil (F-1921-2018, F-1873-2013) vs. ground Mediterranean oregano and whole fennel seed (F-2329-2015, F-1994-2019). The log's Produce rule mentions "herbs" without qualification, which would swallow the entire spice trade.

**Plain meat cuts — rules hold, but the sample cannot really test them.** FDA recall records under-represent raw single-ingredient meat because most of it is USDA-jurisdiction. What the sample actually contains is deli meat ("CITTERIO PROSCIUTTO," "KRAKUS Imported Polish Ham," "D&W LONDON BROIL ROAST BEEF" — dozens of "this is a deli service item" rows), pre-cooked steaks (F-2556-2017), sliced roast beef (F-0851-2024), bulk skinless chicken (H-1139-2026), and dry sausage (F-1023-2019). All handled correctly by the merged label. **I cannot confirm the rules against raw primal cuts, because the sample contains essentially none** — that gap is structural to the data source, not to the taxonomy.

---

### Q3 — Oils/Fats: rule confirmed, boundary rewritten

**Resolution: keep `Oils/Fats` as written; it survives contact with real data. Add an explicit boundary section, because every ambiguous row in the exhaustive block is a boundary case, not a definition case.**

**Confirming evidence.** The `exhaustive:Oils/Fats` block is dominated by exactly what the log described: 35-lb foodservice frying oil and liquid shortening (Bunge, Oasis Foods, Chef's Quality, Silver Source, Old World, Daily Chef, Burger King, Yum, Nathan's, Pocahontas, Frosty Acres, Masbia, EB Golden Fry — 25+ rows), plus soybean/canola/corn oil, extra-virgin olive oil (Bertolli/Carapelli F-0736-2016, McEvoy Ranch F-1621-2018, Daniele 3L H-0253-2025), liquid margarine (Sysco Classic, F-0780-2019), and hemp seed oil (F-1505-2020). No revision needed to the core rule.

**Revised boundary — Oils/Fats vs. Spices/Condiments (and everything else).**

> **The oil must be the product, not the medium and not an ingredient.**
> - **Oils/Fats:** cooking, frying, and salad oils; olive oil; liquid and solid shortening; lard, tallow, ghee; margarine and vegetable-oil butter substitutes; culinary infused oils where the oil is what you buy and use (garlic oil, chili oil sold as oil).
> - **Not Oils/Fats — food packed *in* oil.** The packing medium never governs. Hungarian hot peppers in oil (F-0474-2016, F-0497-2016, F-0478-2016) → `Produce`. Apetina marinated olives & feta in olive oil (F-2248-2019) → `Produce`. Edamame in oil (F-1052-2016) → `Plant Protein`.
> - **Not Oils/Fats — emulsified or seasoned oil-based products.** Dressings, vinaigrettes, mayonnaise, aioli, pesto, marinades, and sauces → `Spices/Condiments`, even at 60%+ oil. "Rosemary & Olive Oil Seasoning" 50 lb (F-0586-2015) → `Spices/Condiments`.
> - **Butter is Dairy; margarine is Oils/Fats.** This split is arbitrary-looking but stable and shelf-accurate. "Beyond Premium Liquid Butter Alternative — soybean oil, hydrogenated soybean oil, TBHQ" (F-0742-2017) → `Oils/Fats`.
> - **Oil in a supplement dosage form → Supplements.** "Full Spectrum Cold Pressed Hemp Oil Gummies" (F-0417-2024, F-0418-2024) → `Supplements`.
> - **Oil as one component of a manufacturing input → Food Additives/Ingredients.** "Prime CAP Sugar, Encapsulated Sugar: sugar and hydrogenated palm oil, 125 lb poly-lined drum" (F-2088-2016) → `Food Additives/Ingredients`.
> - **Oil named in a finished snack → the snack's label.** "Cheddar Kettle Corn — corn, corn oil, sugar, salt, cheddar powder" (F-0773-2024) → `Snacks/Candy`.

**One residual gray zone I am not resolving cleanly:** an edible oil sold by an herbal/therapeutic brand with no explicit claim on the row (Sundial Hemp Seed Oil, F-1505-2020). Default to `Oils/Fats` absent a structure/function claim; route to `Supplements` if the description carries one. Expect a small error rate here.

---

### Q4 — Taxonomy reconciliation: relabel everything

**Resolution: confirmed. Relabel the full dataset under the new taxonomy. Do not map old labels forward.**

The log's recommendation was made cautiously, without having seen a keyword-labeled row. Having now seen ~5,000 of them, the case is stronger than the log assumed: **the keyword labels contain systematic, non-mappable errors.** A forward mapping preserves them, because the defect is in the row assignment, not in the label vocabulary. Specific classes of error in the attached sample:

| Error class | Example rows | Keyword label | Correct label |
|---|---|---|---|
| Buns matched on "hamburger" | F-1559-2013, F-1560-2013, F-1561-2013, F-1564-2013, F-1567-2013, F-1570-2013 through F-1573-2013, F-2968-2015, F-2969-2015, F-3366-2017, F-2250-2019, F-0078- through F-0082-2022, F-0957-2021, F-0215-2022, F-1601-2023, F-0099-2025 (~22 rows) | `Beef` | `Bakery` |
| Seasonings named after a meat | F-1197-2023 "BEEF RUB X1 50 BAG", F-1214-2023 "INJECT FOR CAJUN TURKEY", F-1189/1191/1192-2023 roast-beef rub/inject, F-1119/1132/1172/1221-2023 chicken marinades, F-1313/1314/1347-2015 Bubba's rubs, F-0160-2022, F-0049/0050-2023, F-1219-2023, F-1174-2023 | `Beef` / `Pork` / `Poultry/Eggs` | `Spices/Condiments` |
| Deli sandwiches named after their filling | the entire Fresh Creative Cuisine / Quick & Fresh / Bistro To Go / Orchard Bistro / In Reach / Ukrop's / Premo run (100+ rows) | `Pork` / `Poultry/Eggs` / `Beef` | `Prepared/Frozen` |
| Plant analogs matched on the imitated animal | F-0284/0285-2025 Impossible sausage, F-2240-2015 "Quesadilla, Vegan Beef", F-0379-2020 "STIR FRY BEEF VEGAN", F-0748-2023 Chickenless Tenders, F-0911-2018 Vegan Buffalo Chicken Bites, F-1881-2017 Braised Bean Curd (Mock Chicken), F-0396-2020 "Chick'n General Tso" | `Beef` / `Pork` / `Poultry/Eggs` | `Plant Protein` |
| Brand-name false positive | F-1744-2014 "**Net Food Turkey** Dried Apricots" | `Poultry/Eggs` | `Produce` |
| Pack medium false positive | F-0474-2016, F-0478-2016, F-0497-2016 peppers in oil; F-1052-2016 edamame in oil | `Oils/Fats` | `Produce` / `Plant Protein` |
| Non-food inside food records | H-0058-2026 aluminum milk pan & kadai; F-1515-2024 decorative Indigenous Collection plates; F-2929-2015 pint glasses; F-1752-2019 Freshpet dog treats; F-1271-2013 Opalescence tooth-whitening kit | `Dairy` / `Snacks/Candy` / `Poultry/Eggs` / `Produce` | `Non-Food Item` |
| Deli salad matched on a grain word | F-0983-2014, F-1043-2014, F-1001-2024, F-1804/1805-2024, F-2447-2012 macaroni salad | `Bakery` | `Prepared/Frozen` |

There is no old→new mapping function that fixes any of these, because `Beef → Bakery` is correct for the bun rows and wrong for the beef rows.

**Operational recommendation:** relabel all rows from `product_description` under the 20-label set; retain the original keyword label in a separate `legacy_category` column for diff-based QA only; **do not feed the legacy label to the classifier**, to avoid anchoring it on the errors above.

---

## Coverage-hole rules

### 1. Alcohol → `Beverages`
> Beer, wine, cider, spirits, hard seltzer, and ready-to-drink cocktails go to `Beverages`. No new label: FDA-jurisdiction alcohol recalls are rare (TTB regulates most), and the sample confirms it — of ~230 `coverage_hole:alcohol` rows, only a handful are actually alcoholic (Square Mile Hopped/Original Hard Apple Cider, F-1784-2013 and F-1785-2013; Apple Orchard Crisp Apple Hard Cider, F-0832-2017).

**Corollary that does the real work:** *alcohol as a flavor, ingredient, or batter never changes the category.* Rum raisin ice cream → `Dairy`. Beer bread mix and wine brownie mix (the Rabbit Creek block, ~40 rows) → `Bakery`. Port wine cheese and whiskey cheddar → `Dairy`. Beer-battered cod → `Seafood`; beer-battered onion rings → `Produce`. Vodka sauce → `Spices/Condiments`. Herring in wine sauce → `Seafood`.

**Sub-rule for the mixer block:** **non-alcoholic cocktail mixers, drink syrups, and drink concentrates → `Beverages`**, regardless of bottle size. The Urban River Spirits run (F-1615- through F-1638-2024) was split by the keyword pass across `Produce`, `Beverages`, `Snacks/Candy`, and `Spices/Condiments`; all 24 rows are one product line and all are `Beverages`, including the 5 oz infused simple syrups. Table syrup, pancake syrup, and dessert sauces remain `Spices/Condiments`.

### 2. Coffee creamer → `Beverages`
> All coffee creamers — dairy, non-dairy, plant-based, liquid, or powdered — go to `Beverages`.

Rationale: a creamer is consumed only as a beverage component, and classifying by base would split an identical product across `Dairy`, `Plant Protein`, and `Beverages` for no analytic gain. The keyword pass demonstrated exactly this failure: Coffee-Mate French Vanilla → `Beverages` (F-1687-2019) while International Delight French Vanilla → `Dairy` (F-1784-2019), and Silk Almond Creamer → `Dairy` (F-1877-2019) while Coffee-Mate Almondmilk Creamer → `Beverages` (F-1696-2019).

Scope also covers powdered non-dairy creamer sold as such (Kraft, Libby's, Country Barn, Golden Flag — F-2787-2015; MO-CHA Premium Non-Dairy Creamer — F-0732-2025) and instant milk-tea / latte / 3-in-1 coffee powders built on non-dairy creamer (F-0727-2015, F-0034-2018, F-1615/1616/1618-2018, F-0931- through F-0935-2025).

**Exception:** *creamer stabilizer and emulsifier systems* → `Food Additives/Ingredients`. Grindsted Creamer 2103 / 2160 / 2395 / 1817 (F-1316-2024, F-1318-2024, F-1314-2024, F-1338-2024) are 50 lb hydrocolloid systems used to *manufacture* creamer; they contain no creamer.

### 3. Broth / stock / bouillon → **split by concentration**
> **Ready-to-use liquid broth, stock, and bone broth → `Prepared/Frozen`.** **Concentrated bases, bouillon cubes/granules/powders, and soup bases → `Spices/Condiments`.**
> Test: *if it is poured and consumed or cooked with at strength, it is a prepared food; if it is diluted or dosed by the teaspoon as flavoring, it is a condiment.*

Rationale: the log already routes soups to `Prepared/Frozen`, and cartoned broth is a soup you cook with — Central Market Organic Chicken Broth (F-0732-2024), Imagine Bone Broth (F-0731-2024), Trader Joe's Turkey Stock (F-0723-2024), Great Value Chicken Broth (F-0407-2025), Sprouts Organic Low Sodium Vegetable Broth (F-0728-2024), and the multi-brand reduced-sodium broth rows (F-0722-2024, F-0726-2024, F-0727-2024, F-0729-2024, F-0730-2024, F-0733-2024, F-0736-2024). Bases and cubes are unambiguously seasoning — National Foods Chicken Base 25/50 lb (F-0227-2017, F-0228-2017), "G54703 CHICKEN BASE X2 50.00 BAG" (F-1142-2023), Karlin Chicken Base (F-1114-2023), Herb-Ox granulated bouillon (F-0554-2018), Spice Supreme beef bouillon cubes (F-0572/0573-2018), Maggi chicken bouillon tablets (F-0797-2016), Rapunzel vegetable bouillon (F-0524-2018), Frontier vegetarian broth powder (F-2367-2015, F-2368-2015), Orrington Farms chicken broth base (F-0705-2015).

**Corollary:** the animal in the name does not make it meat. Chicken broth is not `Beef/Pork/Poultry/Game Meats`; the keyword pass put every one of these rows there.

### 4. Baby food (non-formula purees) → **new label `Baby/Toddler Food`**
> Infant and toddler purees, pouches, and jarred baby food; infant cereal; teething and toddler snacks explicitly marketed for infants/toddlers; **and all infant and toddler formula, regardless of protein base.**

Rationale for a new label rather than ingredient-based routing: the sample shows one product line fragmenting three ways under ingredient logic. Within the single Plum Organics 2014 recall, `Blueberry, Pear & Purple Carrot` → `Produce`, `Blueberry, Parsnip & Buckwheat` → `Grains/Cereal`, and `Mango, Carrot & Greek Yogurt` → `Dairy` (F-0365-2014, F-0373-2014, F-0376-2014). That is precisely the fragmentation the log's governing principle exists to prevent, and baby food is a distinct hazard population (heavy metals, *Cronobacter*) whose recalls analysts will want as one bucket.

**This supersedes the log's formula rule.** The log split formula by protein source (milk → `Dairy`, soy/amino-acid → `Plant Protein`), which produces the same fragmentation across a single product family: Similac Sensitive, Similac Organic with A2 Milk, Similac For Spit Up, Enfamil Nutramigen (F-0809-2024), Bobbie (F-1486-2019), HiPP (F-0914-2021), Holle Goat (F-0919-2021), Sammy's Milk (F-1724-2017), Mt. Capra Goat Milk Formula Kit (F-1347-2024). All → `Baby/Toddler Food`.

**Boundaries:** adult medical/enteral nutrition is *not* baby food (→ `Supplements`, see below). A cracker or puff sold to the general market is `Snacks/Candy` even if toddlers eat it; the label must be infant/toddler-directed.

### 5. Honey → `Spices/Condiments` (with a hard Supplements carve-out)
> Pure honey, raw honey, comb honey, creamed/whipped/spun honey, and flavored or infused honey sold as honey → `Spices/Condiments`, alongside jams, jellies, and syrups.

Evidence: Bee Well Wildflower (H-0664-2026), Goya Honey with Comb (F-2602-2016), Vintage Pure Bee Flower Honey (F-0765-2015), the Dakota Honey Company spun-honey line (H-0768- through H-0772-2026), and the large creamed/whipped honey run (H-0702- through H-0710-2026, H-0382- through H-0384-2025) — which the keyword pass scattered across `Spices/Condiments`, `Produce`, `Dairy`, and `Snacks/Candy` purely on flavor words ("Raspberry," "Cinnamon," "Salted Caramel").

**Corollary:** honey as an ingredient never governs. Honey-roasted peanuts → `Nuts/Seeds`. Honey wheat bread → `Bakery`. Honey mustard dressing → `Spices/Condiments` (as a dressing, not as honey).

**Carve-out — claim-bearing honey sachets → `Supplements`.** The sample contains the entire tainted-sexual-enhancement honey class, and it must not be filed as a condiment: Kingdom Honey Royal Honey VIP (F-1514-2022), Dose Vital Vital Honey with Caviar and Tongkat Ali (F-1515-2022), Jaguar Power Honey (F-0861-2022), Helmi Honey VIP (F-0862-2022), Boner Bears Honey Male Enhancement (H-0653-2026), and the Comvita Manuka + Reishi / Lion's Mane / Cordyceps line (H-0014- through H-0016-2025). **Test: honey in single-serve sachets with performance, energy, or therapeutic claims, or honey blended with a botanical/functional extract → `Supplements`.**

### 6. Agave / stevia / molasses → `Spices/Condiments` (nutritive) with two exceptions
> **All sweeteners sold as sweeteners → `Spices/Condiments`:** honey, molasses, agave nectar, maple syrup, cane and coconut syrups, table syrups, and consumer stevia/monk-fruit.
> **Exception A — dry crystalline baking sugars remain `Baking Supplies`** (granulated, brown, cane, powdered, sanding sugar), per the log.
> **Exception B — purified sweetener compounds sold in bulk to manufacturers → `Food Additives/Ingredients`** (Reb M, erythritol, sorbitol, sucralose, allulose in drums/totes).

**Stated test for A vs. the main rule:** *dry crystalline sugar you bake with → `Baking Supplies`; liquid or viscous sweetener you pour at the table or spread → `Spices/Condiments`.*

Evidence for B: "4M DF NSA Semisweet Baking Drop — Chocolate Liquor, Inulin, Erythritol… Stevia Leaf Reb M, 40 lb poly-lined case" (F-0438-2023) is a manufacturing input; the sweetener rows inside it are not a table product.

**One trap:** "Good Herbs, Inc., STEVIA, 1 oz bottle" (F-0422-2015) is an herbal tincture from a supplement house, one row in a run of 80+ Good Herbs tinctures → `Supplements`, not `Spices/Condiments`. **Test: a sweetener in a supplement dosage form, from a supplement brand, follows the dosage form.**

---

## New collisions found

Eight collisions beyond the log's 10 documented boundary rules. Each is high-volume in this sample.

**1. Meat-named seasonings, rubs, marinades, injections, cures, and gravy mixes → `Spices/Condiments`.**
The single largest source of wrong meat labels. Rows: `S04380 BEEF RUB X1 50.00 BAG` (F-1197-2023), `S18149 INJECT FOR CAJUN TURKEY X1` (F-1214-2023), `S00527 / S01056 RUB FOR ROAST BEEF` (F-1189-2023, F-1191-2023), `G94311 SAVORY CHICKEN MARINADE MIX` (F-1172-2023), `G76586 CHICKEN INJECT` (F-1157-2023), Turkey Dripping Type Marinade 50 lb (F-1684-2012), Grilled Chicken Marinade IFF 3559317 (F-1232-2013), Carolina Ingredients Beef Gravy Mix 50 lb (F-0160-2022), Karlsburger NSLP Beef and Turkey Gravy Mix (F-0049-2023, F-0050-2023), Hillcrest Farms Poultry Gravy Mix 25 lb (F-0226-2017), HyVee Turkey Gravy (F-0501-2024), Bubba's Bar-B-Q Rub Multi-Purpose Beef/Pork/Chicken (F-1313-, F-1314-, F-1347-2015), Adams Brisket Rub (F-1307-2015), Culinary Masters Steak Rub (F-2002-2015).
**Sub-rule:** *nitrite curing blends are functional, not flavoring → `Food Additives/Ingredients`* — Newly Weds `R03810 LOEFFLER COMP PORK ROLL CURE X1 54 lbs` (F-1444-2023), `R03361 HAHN'S SPECIAL BACON CURE HS X1 40 lbs` (F-1445-2023), The Sausage Maker Instacure #1 (F-0405-2024). Likewise `G94866 Stuffed Crab Seasoning X1 34.45 lbs` (F-0534-2021) → `Spices/Condiments`, not `Seafood`.

**2. Deli sandwiches, subs, hoagies, wraps, paninis, pinwheels, and boxed lunches → `Prepared/Frozen`.**
The log's composite rule already covers this, but the collision is worth naming because it is the largest single relabeling delta in the dataset. 100+ rows across Fresh Creative Cuisine, Quick & Fresh, Bistro To Go, Orchard Bistro, In Reach, Westin Label, Dietz & Watson, Ukrop's, Premo, Wakefield, and the entire 2015 "MFG Code" convenience-sandwich run (F-0810- through F-0917-2015). Keyword sent them to `Pork`, `Poultry/Eggs`, `Beef`, `Seafood`, `Bakery`, and `Grains/Cereal` depending on which word matched first.

**3. Plant-based analogs — classify by what they are made of, not what they imitate.**
- Legume/soy/pea/wheat-gluten meat, egg, cheese, and yogurt analogs → `Plant Protein`: Impossible Savory/Spicy Ground Sausage "Meat from plants" (F-0284-2025, F-0285-2025), Cena Vegan Pollo Asado (vital wheat gluten, F-2154-2019), Just Egg Spring Greens (F-1510-2022), "Quesadilla, Vegan Beef" (F-2240-2015), "STIR FRY BEEF VEGAN" (F-0379-2020), Trader Joe's Chickenless Crispy Tenders (F-0748-2023), Braised Bean Curd (Mock Chicken) (F-1881-2017), WayFare dairy-free pudding (F-0464-2020, F-0465-2020), Goodles vegan white cheddar (H-0027-2026).
- **Plant milks and plant creamers → `Beverages`** (consistent with the creamer rule): Oatly (F-1675-2022), Ripple pea milk (F-0921-2018), Rise Brewing Organic Oatmilk (F-0734-2024), almond/soy/cashew beverages.
- **Non-dairy frozen desserts → `Prepared/Frozen`**: Enlightened Dairy-Free (F-1027-2020), Full Circle coconutmilk frozen dessert (F-1702-2024), Van Leeuwen Vegan Oat (F-1739-2024), Dream Pops (F-0384-2022, F-0385-2022).
*Accepted cost, stated openly:* this last line puts an ice cream and its vegan twin in different labels. That is the price of never calling a coconut product "Dairy." If downstream analysis is frozen-dessert-centric, a dedicated `Frozen Desserts` label would be the fix — but I am not adding one on this evidence.

**4. Dressed deli salads — split by what dominates.**
Keyword sent macaroni salad → `Bakery`, potato salad → `Produce`, tuna salad → `Seafood`, egg salad → `Produce`. Resolve as:
- **Grain/pasta-based** (macaroni, pasta, orzo, quinoa, couscous, Thai noodle salad) → `Prepared/Frozen`: F-0983-2014, F-1001-2024, F-1804-2024, F-1805-2024, F-1310-2023, F-1848-2018.
- **Potato-based** → `Prepared/Frozen`: the large Reser's / Garden-Fresh / Finest Traditions potato-salad run (F-0239-2014, F-0247-2014, F-0259-2014, F-0928-2014, F-0971-2014, F-0489-2014, F-1029-2018). *This moves potato salad out of `Produce`.*
- **Protein-dominant** → the protein label: tuna salad → `Seafood` (F-1212-2014, F-1216-2014, F-1218-2014, F-0965-2020), chicken salad → meat label, egg salad → `Eggs`.
- **Vegetable-dominant, lightly dressed** → `Produce` (coleslaw, cucumber salad) or `Plant Protein` (three-bean, calico bean), per existing rules.

**5. Hummus and dips — three-way split, currently scattered.**
The log assigns hummus to `Plant Protein`, but the keyword pass filed it as `Spices/Condiments` (the Sabra rows, F-1111-2017, F-1113-2017, F-1123-2017), `Produce` (Pita Pal, F-1584-2016, F-2205-2019), and `Nuts/Seeds` (F-0070-2019). Affirm and extend:
- Legume-based dips (hummus, black bean dip, edamame dip, falafel) → `Plant Protein`.
- Cheese- and cream-cheese-based dips and spreads → `Dairy`: pimento cheese dip (F-1281-2020), Jarlsberg jalapeño dip (F-1282-2020), deli ranch cheese spread (F-1291-2020), queso, cheese balls.
- Vegetable/sauce dips (salsa, ranch, French onion, spinach-artichoke, tapenade) → `Spices/Condiments`.

**6. Adult medical nutrition and thickened beverages → `Supplements`.**
The log says "medical foods sold to consumers" → `Supplements`, but the sample shows this class scattered badly. Rows: Lyons and Sysco Imperial Thickened Dairy Drink, honey consistency (F-1612-2022 → `Supplements`, F-1631-2022 → `Supplements`) vs. Lyons/Imperial Thickened Apple and Cranberry Nectar (F-0052-2023, F-0058-2023, F-0059-2023, F-0061-2023 → `Beverages`/`Produce`) — the same product family, four labels. Also Nestlé Nutren 2.0 (F-0261-2025 → `Beverages`), Glucerna (F-1602-2022 → `Snacks/Candy`), Kate Farms Nutrition Shake (F-1668-2022 → `Snacks/Candy`), enterade Advanced Oncology Formula (F-0999-2023 → `Beverages`), Functional Formularies Nourish peptide formula (H-1153-2026 → `Plant Protein`).
**Rule: medical foods, oral nutritional supplements, enteral formulas, and dysphagia-thickened beverages → `Supplements`.**

**7. Protein powders and RTD protein shakes → `Supplements`, regardless of protein source.**
This *changes* the log, which routed plant protein powders to `Plant Protein`. Collision rows: Premier Protein shakes (F-1625-2022 → `Prepared/Frozen`, F-0382-2023 → `Prepared/Frozen`), Evolve Vanilla Bean Plant-Based Protein Shake (F-0538-2021 → `Plant Protein`), Tone It Up Plant-Based Protein Shake (F-1651-2022 → `Plant Protein`), Muscle Milk (F-0343-2017 → `Bakery`, F-0334-2017 → `Produce`, F-0346-2017 → `Snacks/Candy`), Isomorph 28 Whey Isolate (F-0509-2021, F-0500-2021 → `Supplements`), Aivia Whey Protein+ (F-1540-2022 → `Snacks/Candy`).
**Test: protein in a supplement format — tub with a scoop, Supplement Facts panel, "Dietary Supplement" statement, or single-serve RTD shake — → `Supplements`. Protein sold as a manufacturing ingredient (soy protein isolate in 50 lb bags, TVP, pea protein 20 kg) → `Plant Protein` or `Food Additives/Ingredients`.**

**8. Non-food already present inside these records → `Non-Food Item`.**
Confirmed and extended to two categories the log did not name: **pet food and pet treats** (Freshpet Dog Joy Chicken Treats, F-1752-2019, keyword `Poultry/Eggs`) and **oral-care / cosmetic kits** (Opalescence Treswhite Supreme Peach Patient Kit, F-1271-2013, keyword `Produce`). Plus cookware (H-0058-2026 aluminum milk pan and kadai, keyword `Dairy`), tableware (F-1515-2024 Indigenous Collection decorative plates, keyword `Dairy`), and drinkware (F-2929-2015 pint glasses, keyword `Snacks/Candy`).

*One collision I looked for and did not find:* the log's `Baking Supplies` vs. `Food Additives/Ingredients` boundary held up cleanly across every row I checked. No revision needed.

---

## Summary table

**How to read the count column.** These are estimates from scanning the attached rows' existing `category` values, not a per-row re-tally under the new taxonomy — the task did not require per-row output, and I will not report precision I did not compute. **More importantly: these counts are sample-design artifacts, not population frequencies.** Five categories were sampled exhaustively, six product types were sampled by keyword hole, and eleven were sampled proportionally. Nothing here supports a claim about relative recall volume in the full dataset.

| Label | Rows in this sample (est., by legacy `category`) | Status vs. the log's 18 |
|---|---|---|
| **Dairy** | ≈250–320 (stratified; plus creamer, alcohol, baby-food rows that will move) | **Changed** |
| **Eggs** | ≈60–90, all drawn out of the `exhaustive:Poultry/Eggs` block | **New** |
| **Beef/Pork/Poultry/Game Meats** | ≈250–320 combined across legacy `Beef`, `Pork`, `Poultry/Eggs` (exhaustive) — but a large minority will move to Bakery, Prepared/Frozen, Spices/Condiments, Eggs, and Plant Protein | **Changed** (merged label; scope tightened) |
| **Seafood** | ≈150–200 (stratified; plus beer-battered fish from the alcohol hole) | Unchanged (clarified) |
| **Produce** | ≈250–320 (stratified; plus peppers-in-oil, baby-food, honey rows) | Unchanged (clarified) |
| **Plant Protein** | ≈45–60 (exhaustive) + analogs arriving from legacy meat labels | **Changed** |
| **Grains/Cereal** | ≈100–140 (stratified) | Unchanged |
| **Bakery** | ≈200–260 (stratified) + ≈22 bun rows arriving from legacy `Beef` + ~40 beer/wine bread-and-brownie mixes | Unchanged |
| **Prepared/Frozen** | ≈130–170 (stratified) + large inflows: deli sandwiches, liquid broth, pasta/potato salads, non-dairy frozen desserts | **Changed** |
| **Snacks/Candy** | ≈150–200 (stratified) | Unchanged |
| **Nuts/Seeds** | ≈150–200 (stratified) | Unchanged |
| **Beverages** | ≈120–160 (stratified) + ≈57 coffee-creamer rows + cocktail mixers + plant milks + the handful of true alcohol rows | **Changed** |
| **Spices/Condiments** | ≈150–200 (stratified) + honey + bouillon/bases + meat-named seasonings | **Changed** |
| **Oils/Fats** | ≈40–55 (exhaustive), minus ~5 peppers/edamame-in-oil rows leaving | Confirmed (boundary added) |
| **Supplements** | ≈150–200 (stratified) + medical foods, protein powders, claim-bearing honey, kratom | **Changed** |
| **Baking Supplies** | Low in this sample; not separately sampled | Unchanged |
| **Food Additives/Ingredients** | Low in this sample (~10–20 identifiable: Grindsted systems, IFF flavor codes, encapsulated sugar, cures, MILK-N-EGG mix) | **Changed** |
| **Non-Food Item** | ≈5–10 identifiable, all currently mislabeled as food | **Changed** |
| **Baby/Toddler Food** | ≈25–35 (the `coverage_hole:baby_food` block) + ≈10–15 formula rows currently inside `Supplements`/`Dairy` | **New** |
| **Uncategorized** | Not sampled as a category; the sample contains ~5–10 genuinely unclassifiable rows (multi-product firm-wide recalls such as H-0411-2026, F-1523-2022, F-1531-2022, F-1461-2023) | Unchanged |

---

### Two things I could not resolve on this sample

1. **Raw single-ingredient meat cuts remain untested.** FDA recall records are structurally thin here (USDA jurisdiction). The merged meat label is validated against deli meat, cured meat, jerky, and cooked cuts only.
2. **`Baking Supplies` has almost no direct evidence in this sample either.** It was not among the exhaustive, coverage-hole, or stratified categories, and I inferred its boundaries from adjacent rows (encapsulated sugar, food colors, confectionery coatings, chocolate wafers). If a third validation pass is run, sample it deliberately — it and `Food Additives/Ingredients` are now the two least-evidenced labels in the set.