# Building Lore — User Guide

This guide explains how to use the Building Lore plugin in-game. Building Lore lets you select 3D regions of blocks, save them as named selections, serialize them into shareable tokens, and export their block data to files.

---

## Getting Started

### Permission

You need the `buildinglore.use` permission to use most commands. Exporting block data additionally requires the `buildinglore.export` permission (operators have this by default).

### Obtaining the Wand

Run the following command to receive a **Selection Wand** (a golden-named wooden axe):

```
/bl wand
```

The wand will appear in your inventory.

---

## Selecting a Region

A region is a 3D box (cuboid) defined by two opposite corners.

### Using the Wand

With the Selection Wand in hand:

- **Left-click a block** — sets **Corner 1** to that block's position.
- **Right-click a block** — sets **Corner 2** to that block's position.

A chat message confirms each corner. Once both corners are set, the plugin displays the region's coordinates and block volume. Particle outlines will automatically appear around your selection so you can see its boundaries.

### Using Commands

If you prefer not to use the wand, you can set corners to your current standing position:

```
/bl pos1
/bl pos2
```

These work the same way — once both are set, you'll see a volume preview.

> **Note:** Both corners must be in the same world.

---

## Saving Selections

A **selection** is a named collection of one or more regions. You can build complex shapes by adding multiple cuboid regions to the same selection.

### Adding a Region

After setting both corners, save the region to a selection:

```
/bl add <name>
```

- If a selection with that name doesn't exist yet, it is created automatically.
- If it already exists, the new region is appended to it.
- The selection is saved to disk immediately.

**Example:**

```
/bl add townhall
```

You can keep adjusting your corners and running `/bl add townhall` to attach more regions to the same selection.

### Removing a Region

To remove a specific region from a selection by its index (0-based):

```
/bl remove <name> <index>
```

Use `/bl info <name>` first to see region indices.

---

## Viewing Your Selections

### List All Selections

```
/bl list
```

Shows every selection you own, including its name, number of regions, total block volume, and world.

### Detailed Info

```
/bl info <name>
```

Displays full details for one selection: world name, total volume, and each region with its index, corner coordinates, and individual volume.

---

## Particle Visualization

When you use the wand, particle outlines are automatically turned on so you can see your current selection boundaries in the world.

You can also toggle the particle display manually at any time. (Visualization only shows your current wand corners, not saved selections.)

---

## Serializing & Sharing

### Serialize

Convert a saved selection into a compact text token you can copy and paste:

```
/bl serialize <name>
```

This outputs a token in the format:

```
[BL:world_name|x1,y1,z1>x2,y2,z2|...]
```

You can paste this token into books, signs, chat, or external documents to share the selection with others.

### Import

Recreate a selection from a token:

```
/bl import <token>
```

The imported selection is saved under the name **"imported"**.

**Example:**

```
/bl import [BL:world|10,64,20>30,80,40]
```

---

## Exporting Block Data

Export the actual block-by-block data of a selection to a text file:

```
/bl export <name>
```

- Requires the `buildinglore.export` permission.
- The file is saved to `plugins/BuildingLore/exports/<your-uuid>/<name>.txt`.
- Air blocks are skipped automatically.

Each line in the exported file records a block's position, type, and state:

```
x,y,z | minecraft:block_type | [state=value,...]
```

---

## Deleting a Selection

To permanently remove a saved selection:

```
/bl delete <name>
```

This removes the selection from both disk and memory.

---

## Command Reference

| Command | Description |
|---|---|
| `/bl wand` | Get the Selection Wand |
| `/bl pos1` | Set corner 1 to your position |
| `/bl pos2` | Set corner 2 to your position |
| `/bl add <name>` | Save current region to a selection |
| `/bl remove <name> <index>` | Remove a region by index |
| `/bl list` | List all your selections |
| `/bl info <name>` | Show details of a selection |
| `/bl delete <name>` | Delete a selection |
| `/bl serialize <name>` | Get a shareable text token |
| `/bl import <token>` | Create a selection from a token |
| `/bl export <name>` | Export block data to a file |

---

## Tips

- **Tab completion** is supported — press Tab after `/bl` to see available subcommands, and again after subcommands that take a name to see your existing selections.
- You can build complex, non-rectangular shapes by adding multiple regions to the same selection.
- Regions that overlap or are adjacent on the same plane are handled automatically — overlapping areas won't be double-counted, and touching regions may be merged.
- Selections are saved per-player and persist across server restarts.
