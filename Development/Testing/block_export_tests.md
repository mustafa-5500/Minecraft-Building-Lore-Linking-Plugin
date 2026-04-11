# Block Data Export Tests

## Test 1: Export a Simple Selection
1. Create a selection around a small known structure (e.g. a 5x5x5 area)
2. Run `/bl export myhouse`
3. **Expected:** Success message with file path
4. Open the file at `plugins/BuildingLore/exports/<uuid>/myhouse.txt`
5. Verify the header contains selection name, world, region count, volume

## Test 2: Verify Block Data Format
1. Open the exported file
2. **Expected:** Each non-air block has a line like:
   ```
   x,y,z | minecraft:stone_bricks
   x,y,z | minecraft:oak_door | [facing=east,open=true,half=upper]
   ```
3. Verify coordinates fall within the selection bounds

## Test 3: Air Blocks Skipped
1. Export a selection that includes open air
2. **Expected:** No lines with `minecraft:air` in the output file

## Test 4: Block States Included
1. Build a small structure with state-bearing blocks (doors, stairs, slabs, levers)
2. Export the selection
3. **Expected:** Block state data appears in brackets, e.g. `[facing=north,half=top]`

## Test 5: Multi-Region Export
1. Create a selection with 2+ regions, export it
2. **Expected:** Output file contains `## Region 0: ...` and `## Region 1: ...` sections

## Test 6: Large Selection Warning
1. Create a very large selection (e.g. 100x100x100 = 1 million blocks)
2. Run `/bl export bigarea`
3. **Expected:** The export completes (may take several seconds). Verify no server crash or timeout. File is written.

## Test 7: Export Permission Required
1. Remove op or `buildinglore.export` permission
2. Run `/bl export myhouse`
3. **Expected:** "No permission to export" error message

## Test 8: Export Unloaded World
1. Create a selection, then unload the world (or change the world name in the yml)
2. Run `/bl export myhouse`
3. **Expected:** Error message about the world not being loaded

## Test 9: Overwrite Existing Export
1. Export a selection twice
2. **Expected:** The second export overwrites the first file without error
