# Redstone Block Index

A filterable/sortable catalogue of Minecraft **Java Edition** blocks and their
redstone-relevant properties (piston behavior, water breakage, stability, mob
spawning, solidity, redstone conductivity, collision hitbox size, gravity, and
flammability). Blocks are grouped by behavior family (~238 rows).

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

Java Edition, **1.21.11** (post–"The Copper Age" 1.21.9). Bedrock Edition differs on
several mechanics (e.g. Moss Block, Pumpkin, Melon and Shulker Box are movable by
pistons there but break in Java) and isn't covered. `flammable` is a simplified
indicator of the common cases, not an exhaustive fire-spread model. Always verify
load-bearing technical builds in-game.

### Block coverage / omissions

The row list is cross-referenced against the full block registry for the target version
(the `blocks.json` for `1.21.11` in
[`PrismarineJS/minecraft-data`](https://github.com/PrismarineJS/minecraft-data), an
official-registry mirror). Every non-technical placeable block maps to a behavior-family
row. The most recent pass added the Copper Age blocks (Shelf, Copper Chest, Copper Golem
Statue, Copper Bars/Chain/Lantern, oxidizing Lightning Rod) plus older blocks that had
been unintentionally omitted (Sandstone family, Bricks, Shulker Box, Froglights, Hay/
Honeycomb/Dried Kelp blocks, Tinted Glass, Copper Doors/Trapdoors, Infested Blocks,
Mangrove Roots, Heavy Core, Sniffer Egg, Dried Ghast, and assorted small plants).

### Source of truth per column

| Column(s) | Authoritative source |
| --- | --- |
| `height`, `width`, `solid` | `blockCollisionShapes.json` (machine-extracted `VoxelShape`s from the game). `height` = Y extent, `width` = smaller horizontal (X/Z) extent, `solid` = has any collision box. |
| `conductive` | Full opaque cube rule: 16³ collision **and** opaque (`filterLight == 15` in the block registry). Non-opaque full cubes (Glass, Ice, Slime, Honey, Tinted Glass, Mangrove Roots, Shulker Box, Copper Grate) are `FALSE`. |
| `spawn_hostile`, `spawn_friendly` | Derived from the same registry data: needs a full, opaque, flat top surface (opaque + full-height + solid), matching the game's spawn-placement rules; documented exceptions (Bedrock, Glowstone/Sea Lantern transparency, Slime Block) are in the notes. |
| `stable` | Whether the block presents a full flat top face (full-height, complete 16×16 top) — derived from the collision shape. |
| `falls` | The finite set of gravity-affected blocks (Sand/Red Sand/Suspicious Sand, Gravel/Suspicious Gravel, Concrete Powder, Anvils, Dragon Egg, Pointed Dripstone, Scaffolding). |
| `piston` | The game's per-block `PushReaction` as tabulated on the Minecraft Wiki *Piston* page (Java column): `Immovable` = cannot be pushed / blocks extension; `Breaks` = destroyed & dropped when pushed; `Movable` = normal push. |
| `breaks_water` | Whether flowing water destroys the block (Minecraft Wiki *Water* mechanics). |
| `flammable` | Whether the block has non-zero burn odds in the game's fire registrations (Minecraft Wiki *Fire* / block-properties flammability table). |

`height` and `width` come from `blockCollisionShapes.json`, which is machine-extracted
directly from the Java game's registered `VoxelShape`s (via a data-generator mod) rather
than hand-transcribed — this is real game data, not a guess or a wiki paraphrase. It
caught several genuine errors (e.g. Composter and Cauldron are actually full 16px
collision cubes despite looking hollow; Cobweb and Pressure Plates have *no* collision
box at all; Conduit is a small floating 6px cube, not a full block; Chest/Ender Chest
are 14³, not 16³).

The `piston` column was re-audited against the wiki's push-reaction table this pass,
which corrected several long-standing errors: Moss Block, Pumpkin, Melon, Bed, Decorated
Pot, Bell, Lantern and Scaffolding all **break** when pushed in Java Edition (they were
previously listed as Movable/Immovable).

Caveats on the hitbox data specifically:
- It reflects one representative blockstate per row (e.g. an unconnected fence post, a
  closed door) — grouped "family" rows may hide minor variation between materials or
  states, called out in `height_note`/`width_note` where it matters.
- If you spot another discrepancy, the most reliable way to verify it is the same way
  these fixes were found: pull the block's shape straight from `blockCollisionShapes.json`
  for a recent version rather than trusting prose descriptions (wiki or otherwise).
