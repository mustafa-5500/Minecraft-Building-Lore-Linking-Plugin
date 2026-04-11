**Description:** This plugin allows users to make selection in their worlds, these selections are sets of Cuboid regions, with each Cuboid region being defined by every block coordinate between a min coordinate and max coordinate. From these selections the player can get a text representation of the Set of Cuboid regions, which allows them to link regions in text documents. Furthermore they can get readable text version of the coordinate block data, so in the future the documents and block data can be used to train models.

---

## Platform
- **Minecraft Paper** (Bukkit/Paper API)
- Java 17+
- Built with Gradle or Maven, targeting Paper 1.20+

---

## Existing Code Reference
The `src/` folder contains a **Hytale** land-claiming plugin (`org.almond.lands`) with reusable patterns:
- **`Region`** — Cuboid defined by two `Vector3i` corners. Has `contains`, `overlaps`, `intersection`, `subtract`, `merge`, `isAdjacentTo`, `volume`. This geometry logic transfers almost 1:1; just swap `Vector3i` for Bukkit's `BlockVector` or a custom lightweight `Vec3i`.
- **`SelectionManager`** — Per-player corner1/corner2 state, selection completion. Reusable pattern for this plugin's wand-based selection flow.
- **`Land`** — A named collection of regions. Analogous to this plugin's concept of a "Selection Set" (a named group of cuboid regions a player has defined).

The permissions/roles/members/claims systems are **not needed** for this plugin.

---

## Plugin Architecture

### Package: `org.almond.buildinglore`

```
org.almond.buildinglore/
├── BuildingLorePlugin.java          # Main plugin class (extends JavaPlugin)
├── model/
│   ├── CuboidRegion.java            # Cuboid defined by min/max BlockVector (adapted from Region)
│   └── Selection.java               # Named set of CuboidRegions belonging to a player
├── manager/
│   ├── SelectionManager.java        # Per-player wand state (corner1, corner2, pending region)
│   └── SelectionStorageManager.java # Saves/loads named Selections to disk (YAML or JSON)
├── command/
│   └── BuildingLoreCommand.java     # Single command tree: /bl <subcommand>
├── listener/
│   └── WandListener.java            # PlayerInteractEvent — left/right click to set corners
├── serializer/
│   ├── RegionSerializer.java        # Converts Selection → compact text (for embedding in documents)
│   └── BlockDataExporter.java       # Reads blocks from world in a Selection → readable text output
└── util/
    └── WandUtil.java                # Wand item creation/detection helper
```

---

## Core Components

### 1. CuboidRegion (model)
Adapted from the existing `Region` class:
- Two corners (min, max) stored as integer x/y/z (use Bukkit `BlockVector` or plain int fields)
- `contains(x, y, z)` — point-in-box check
- `overlaps(other)` — AABB intersection test
- `getVolume()` — block count
- `toString()` → compact serialized form, e.g. `(x1,y1,z1)-(x2,y2,z2)`
- `fromString(String)` → parse back
- Also stores **world name** so regions are world-scoped

### 2. Selection (model)
- UUID id
- String name (player-chosen)
- UUID owner (player UUID)
- World name
- `Set<CuboidRegion>` regions
- Timestamp created
- Methods: `addRegion`, `removeRegion`, `getTotalVolume`, `containsBlock(x,y,z)`

### 3. SelectionManager (manager)
Per-player ephemeral state for building regions with a wand:
- `setCorner1(player, location)`
- `setCorner2(player, location)`
- `getCorner1/2(player)`
- `hasComplete(player)` — both corners set
- `buildRegion(player)` → returns a `CuboidRegion` from current corners, then clears state
- Stores state in a `Map<UUID, ...>` (RAM only, no persistence needed)

### 4. SelectionStorageManager (manager)
- `saveSelection(Selection)` — persist to `plugins/BuildingLore/selections/<uuid>.yml`
- `loadSelection(UUID)` / `loadAllForPlayer(UUID)`
- `deleteSelection(UUID)`
- Uses Bukkit `YamlConfiguration` for simplicity

### 5. WandListener (listener)
Listens to `PlayerInteractEvent`:
- **Left-click block** with wand → set corner 1, message player
- **Right-click block** with wand → set corner 2, message player
- Wand = a specific item (e.g., wooden axe or custom-named stick)

### 6. RegionSerializer (serializer)
Converts a `Selection` to a **compact text token** for embedding in documents:
```
[BL:world_name|x1,y1,z1>x2,y2,z2|x3,y3,z3>x4,y4,z4]
```
- Parseable back into a Selection
- Designed to be copy-pasted into lore documents, wikis, etc.
- `serialize(Selection) → String`
- `deserialize(String) → Selection`

### 7. BlockDataExporter (serializer)
Reads actual block data from the world within a Selection's regions:
- Iterates every block coordinate in each CuboidRegion
- Outputs structured text, e.g.:
  ```
  x,y,z | minecraft:stone_bricks | [facing=north,half=bottom]
  x,y,z | minecraft:oak_door      | [facing=east,open=true,half=upper]
  ```
- Options: skip air blocks, include/exclude block states
- `export(Selection, World, options) → String` (could be large, write to file)

---

## Commands

**Base command:** `/bl` (alias: `/buildinglore`)

| Subcommand | Description |
|---|---|
| `/bl wand` | Give the player the selection wand item |
| `/bl pos1` | Set corner 1 to player's current position (alternative to wand click) |
| `/bl pos2` | Set corner 2 to player's current position |
| `/bl add <name>` | Add the current corner1/corner2 as a region to the named Selection (creates it if new) |
| `/bl remove <name> <index>` | Remove a region by index from a Selection |
| `/bl list` | List all of the player's saved Selections |
| `/bl info <name>` | Show details of a Selection (regions, volume, world) |
| `/bl delete <name>` | Delete a saved Selection |
| `/bl serialize <name>` | Output the compact text token for the Selection (copy-pasteable) |
| `/bl export <name>` | Export block data for the Selection to a file in the plugin folder |
| `/bl import <token>` | Parse a compact text token and create a Selection from it |

---

## Permissions

| Permission | Default | Description |
|---|---|---|
| `buildinglore.use` | true | Basic wand and selection commands |
| `buildinglore.export` | op | Export block data (can be expensive) |
| `buildinglore.admin` | op | Manage other players' selections |

---

## Data Storage
- Selections stored as YAML files: `plugins/BuildingLore/selections/<player-uuid>/<selection-name>.yml`
- Block data exports written to: `plugins/BuildingLore/exports/<player-uuid>/<selection-name>.txt`
- No database required

---

## Build Setup
- **Gradle** with `paperweight-userdev` or simple Paper API dependency
- `plugin.yml` defines the `/bl` command and permissions
- Target Paper 1.20.4+ API

---

## Implementation Order
1. Project scaffolding (Gradle, plugin.yml, main class)
2. `CuboidRegion` model (adapt existing `Region`)
3. `Selection` model
4. `SelectionManager` (wand corner state)
5. `WandListener` + `WandUtil` (click to set corners)
6. `/bl wand`, `/bl pos1`, `/bl pos2` commands
7. `/bl add`, `/bl list`, `/bl info`, `/bl delete` commands + `SelectionStorageManager`
8. `RegionSerializer` + `/bl serialize` and `/bl import`
9. `BlockDataExporter` + `/bl export`
10. Permissions, polish, tab-completion