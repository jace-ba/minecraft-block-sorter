# Redstone Block Index

A filterable/sortable catalogue of Minecraft **Java Edition** blocks and their
redstone-relevant properties (piston behavior, water breakage, stability, mob
spawning, solidity, redstone conductivity, collision hitbox size, gravity, and
flammability). Blocks are grouped by behavior family (~211 rows).

## Files

| File | What it is |
| --- | --- |
| `data/blocks.csv` | **Source of truth.** All block data lives here. Edit this. |
| `Redstone_Block_Index.html` | The interactive app (generated data, single self-contained file). |
| `Minecraft_Redstone_Block_Index.xlsx` | Downloadable spreadsheet (generated from the CSV). |
| `scripts/build.py` | Reads the CSV and injects the data into the HTML app. |
| `scripts/export_xlsx.py` | Reads the CSV and regenerates the `.xlsx`. |
| `scripts/validate.js` | Headless smoke test for the built app. |

## Editing the data

`data/blocks.csv` is the one place to change block data. After editing it, rebuild
the generated artifacts:

```bash
python scripts/build.py        # update the web app (Redstone_Block_Index.html)
python scripts/export_xlsx.py  # update the spreadsheet (.xlsx)
```

Then open `Redstone_Block_Index.html` in a browser.

### CSV columns

`name`, `category`, `piston`, `breaks_water`, `stable`,
`spawn_hostile`, `spawn_friendly`, `solid`, `conductive`, `height`, `height_note`,
`width`, `width_note`, `falls`, `flammable`, `notes`, `id`.

- Boolean columns use `TRUE` / `FALSE`.
- `piston` is a single categorical column (replacing the old `movable` +
  `breaks_piston` pair) with exactly one of: `Movable`, `Immovable`, or `Breaks`.
- `height` and `width` are the **collision hitbox** size in pixels (16px = 1 block),
  which can differ from the visual model (e.g. Honey Block is `14`×`14`×`15`, not a
  full cube). `width` is the horizontal footprint (width/length); for blocks whose
  width and length differ, it's a representative value explained in `width_note`.
- `id` is a stable unique slug; keep it unique per row.

## Validating (optional)

```bash
npm install          # installs jsdom (dev dependency)
node scripts/validate.js
```

## Scope & caveats

Java Edition, ~1.21.x (mid-2026), sourced from the Minecraft Wiki (Piston, Falling
Block, Water, Mob spawning, Hitbox, Conductivity) and established redstone mechanics.
Bedrock Edition differs on several mechanics and isn't covered. `flammable` is a
simplified indicator of the common cases, not an exhaustive fire-spread model. Always
verify load-bearing technical builds in-game.

### Data sourcing methodology

Most boolean/categorical columns (piston behavior, water breakage, mob spawning,
conductivity, flammability) are sourced from Minecraft Wiki mechanics pages and spot-
audited against them; a handful of errors found this way have already been corrected
(see git history / `data/blocks.csv` notes column for specifics).

`height` and `width` (collision hitbox size) are cross-checked against
[`PrismarineJS/minecraft-data`](https://github.com/PrismarineJS/minecraft-data)'s
`blockCollisionShapes.json`, which is machine-extracted directly from the Java game's
registered `VoxelShape`s (via a data-generator mod) rather than hand-transcribed — this
is real game data, not a guess or a wiki paraphrase. It caught several genuine errors
(e.g. Composter and Cauldron are actually full 16px collision cubes despite looking
hollow; Cobweb and Pressure Plates have *no* collision box at all; Conduit is a small
floating 6px cube, not a full block; Chest/Ender Chest are 14³, not 16³).

Caveats on the hitbox data specifically:
- It reflects one representative blockstate per row (e.g. an unconnected fence post, a
  closed door) — grouped "family" rows may hide minor variation between materials or
  states, called out in `height_note`/`width_note` where it matters.
- A few very new blocks (e.g. Test Block) aren't in the mid-1.21.x extract used here and
  fall back to visual-model-based estimates.
- If you spot another discrepancy, the most reliable way to verify it is the same way
  these fixes were found: pull the block's shape straight from `blockCollisionShapes.json`
  for a recent version rather than trusting prose descriptions (wiki or otherwise).
