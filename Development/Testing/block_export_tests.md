# Block Data Export Tests

## Test 1: Export a Simple Selection

### Creating a Selection
1. Run `/bl wand` to receive the selection wand (a golden-named wooden axe)
2. Walk to one corner of the structure you want to select (e.g. a 5x5x5 area)
3. **Left-click** a block with the wand to set **corner 1** — you'll see a confirmation message with the coordinates
4. Walk to the opposite diagonal corner of the structure
5. **Right-click** a block with the wand to set **corner 2** — you'll see a confirmation message showing the volume of the selected area
   - *Alternatively*, you can stand at a position and run `/bl pos1` or `/bl pos2` to set corners at your feet without clicking
6. Run `/bl add myhouse` to save the selected region into a new selection called "myhouse"
   - You should see a message confirming the region was added

### Exporting
7. Run `/bl export myhouse`
8. **Expected:** Success message with file path
9. Open the file at `plugins/BuildingLore/exports/<uuid>/myhouse.txt`
10. Verify the header contains selection name, world, region count, volume

## Test 2: Verify Block Data Format

### Prerequisites
- Complete Test 1 so you have an exported file for "myhouse"

### Steps
1. Navigate to the server's `plugins/BuildingLore/exports/<your-uuid>/` folder
2. Open `myhouse.txt` in a text editor
3. **Expected:** Each non-air block has a line like:
   ```
   x,y,z | minecraft:stone_bricks
   x,y,z | minecraft:oak_door | [facing=east,open=true,half=upper]
   ```
4. Note the coordinates in each line — compare them against the corners you selected in Test 1
5. **Expected:** All coordinates fall within the min/max bounds of your selection (no blocks outside the cuboid)

## Test 3: Air Blocks Skipped

### Setup
1. Find or build an area with a mix of solid blocks and open air (e.g. a small house with windows and an open interior)
2. Use `/bl wand` and **left-click** one corner, **right-click** the opposite corner to select the area — make sure the selection includes air space
3. Run `/bl add airtest` to save the selection

### Steps
4. Run `/bl export airtest`
5. Open the exported file at `plugins/BuildingLore/exports/<your-uuid>/airtest.txt`
6. Search the file for `minecraft:air`
7. **Expected:** No lines contain `minecraft:air` — only solid/non-air blocks should appear in the output

## Test 4: Block States Included

### Setup
1. Build a small test structure using blocks that have block states:
   - Place an **oak door** (has `facing`, `open`, `half`, `hinge` states)
   - Place **oak stairs** in different orientations (has `facing`, `half`, `shape` states)
   - Place a **lever** on a wall (has `facing`, `powered` states)
   - Place an **oak slab** as a top slab (has `type` state)
2. Use `/bl wand`, then **left-click** one corner and **right-click** the opposite corner to select the structure
3. Run `/bl add statetest` to save the selection

### Steps
4. Run `/bl export statetest`
5. Open the exported file at `plugins/BuildingLore/exports/<your-uuid>/statetest.txt`
6. Find the lines for the blocks you placed
7. **Expected:** Block state data appears in square brackets after the block type, e.g.:
   - `x,y,z | minecraft:oak_door | [facing=east,open=false,half=lower,hinge=left]`
   - `x,y,z | minecraft:oak_stairs | [facing=north,half=top,shape=straight]`
   - `x,y,z | minecraft:lever | [facing=west,powered=false]`

## Test 5: Multi-Region Export

### Setup
1. Use `/bl wand` and select the **first region** — **left-click** one corner, **right-click** the opposite corner (e.g. the ground floor of a building)
2. Run `/bl add multitest` to create the selection and add this first region
3. Now select a **second, separate region** — **left-click** a new corner, **right-click** the opposite corner (e.g. a detached tower or upper floor)
4. Run `/bl add multitest` again to add the second region to the same selection
5. Run `/bl info multitest` and verify it shows 2 regions

### Steps
6. Run `/bl export multitest`
7. Open the exported file at `plugins/BuildingLore/exports/<your-uuid>/multitest.txt`
8. **Expected:** The file contains separate sections headed `## Region 0: ...` and `## Region 1: ...`, each with their own block data

## Test 6: Large Selection Warning

### Setup
1. Find a large open area in the world (e.g. a flat plains biome)
2. Use `/bl wand` and **left-click** a block at one corner
3. Walk roughly 100 blocks away diagonally and **right-click** a block at the opposite corner — aim for roughly 100x100x100 (1 million blocks)
   - Check the volume shown in the confirmation message
4. Run `/bl add bigarea` to save the selection

### Steps
5. Run `/bl export bigarea`
6. **Expected:** The export completes without crashing the server (may take several seconds and cause a brief lag spike)
7. Verify the file is written to `plugins/BuildingLore/exports/<your-uuid>/bigarea.txt`
8. Check that the server remains responsive after the export finishes (try moving, chatting, breaking a block)

## Test 7: Export Permission Required

### Setup
1. First, create a selection as an op so you have something to export:
   - Use `/bl wand`, select an area, and run `/bl add permtest`
2. Remove your operator status: have another op run `/deop <your-name>`, or use the server console
3. Also ensure you do **not** have the `buildinglore.export` permission (check with a permissions plugin like LuckPerms, or simply being non-op is sufficient since the permission defaults to op)

### Steps
4. Run `/bl export permtest`
5. **Expected:** You receive a "No permission to export" (or similar denial) error message in chat
6. Verify no file was created in the exports folder

### Cleanup
7. Re-op yourself with the server console: `op <your-name>`

## Test 8: Export Unloaded World

### Setup
1. Create a selection in a non-default world (e.g. `world_the_end` or a custom world):
   - Travel to that world, use `/bl wand`, select an area, run `/bl add worldtest`
2. Unload or remove that world:
   - Use a world management plugin (e.g. Multiverse) to unload it: `/mv unload world_the_end`
   - *Alternatively*, manually edit the saved selection YAML at `plugins/BuildingLore/selections/<your-uuid>/worldtest.yml` and change the `world` field to a non-existent world name like `fake_world`

### Steps
3. Run `/bl export worldtest`
4. **Expected:** An error message indicating the world is not loaded or cannot be found
5. Verify no file was created (or the file is empty/incomplete)

## Test 9: Overwrite Existing Export

### Setup
1. Create a selection if you don't already have one:
   - Use `/bl wand`, select a small area, run `/bl add overwritetest`

### Steps
2. Run `/bl export overwritetest` — note the file path in the success message
3. Open `plugins/BuildingLore/exports/<your-uuid>/overwritetest.txt` and note the file size or contents
4. Modify the structure slightly (e.g. break or place a block inside the selected area)
5. Run `/bl export overwritetest` again
6. **Expected:** The command succeeds without errors — no "file already exists" warning
7. Open the file again and verify the contents have changed to reflect the modified structure (confirming the old file was overwritten)
