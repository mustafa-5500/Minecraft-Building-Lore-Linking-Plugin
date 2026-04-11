# Selection Management Tests

## Test 1: Add First Region to New Selection
1. Set corner 1 and corner 2
2. Run `/bl add myhouse`
3. **Expected:** Message confirming region added, total regions: 1, volume shown
4. Verify file created at `plugins/BuildingLore/selections/<your-uuid>/myhouse.yml`

## Test 2: Add Multiple Regions to Same Selection
1. Set new corners for a different area
2. Run `/bl add myhouse`
3. **Expected:** Message showing total regions: 2, combined volume

## Test 3: Add Without Corners Set
1. Clear or don't set any corners
2. Run `/bl add test`
3. **Expected:** Error message telling you to set both corners first

## Test 4: List Selections
1. Create two or more selections with `/bl add`
2. Run `/bl list`
3. **Expected:** All selections listed with name, region count, volume, and world name

## Test 5: List With No Selections
1. Use a player with no saved selections
2. Run `/bl list`
3. **Expected:** Message saying "You have no saved selections."

## Test 6: Info Command
1. Run `/bl info myhouse`
2. **Expected:** Shows selection name, world, total volume, and each region with index, coordinates, and individual volume

## Test 7: Remove Region By Index
1. Run `/bl info myhouse` to see region indices
2. Run `/bl remove myhouse 0`
3. **Expected:** Region 0 removed, confirmation message
4. Run `/bl info myhouse` to verify the region is gone

## Test 8: Remove Invalid Index
1. Run `/bl remove myhouse 99`
2. **Expected:** Error message about invalid index

## Test 9: Delete Selection
1. Run `/bl delete myhouse`
2. **Expected:** Confirmation message
3. Run `/bl list` — the selection should be gone
4. Verify the `.yml` file was deleted from disk

## Test 10: Delete Nonexistent Selection
1. Run `/bl delete doesnotexist`
2. **Expected:** Error message saying selection not found

## Test 11: Tab Completion
1. Type `/bl ` and press Tab
2. **Expected:** All subcommands suggested
3. Type `/bl info ` and press Tab
4. **Expected:** Your saved selection names suggested
