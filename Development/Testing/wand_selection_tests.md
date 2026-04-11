# Wand & Corner Selection Tests

## Test 1: Receive Wand
1. Run `/bl wand`
2. **Expected:** A wooden axe named "Selection Wand" (gold text) appears in your inventory with lore describing left/right click

## Test 2: Left-Click Sets Corner 1
1. Hold the wand
2. Left-click a block
3. **Expected:** Chat message showing "Corner 1 set: X, Y, Z" with the clicked block's coordinates

## Test 3: Right-Click Sets Corner 2
1. Hold the wand
2. Right-click a block
3. **Expected:** Chat message showing "Corner 2 set: X, Y, Z"

## Test 4: Volume Preview After Both Corners
1. Set corner 1 and corner 2 with the wand
2. **Expected:** After the second corner is set, an additional message appears: "Selection volume: N blocks"
3. Verify the volume makes sense (e.g. a 3x3x3 selection = 27 blocks)

## Test 5: Pos1/Pos2 Commands
1. Stand at a known position, run `/bl pos1`
2. Move to another position, run `/bl pos2`
3. **Expected:** Both corners set to your feet position, volume preview shown

## Test 6: Wand Does Not Break Blocks
1. Hold the wand in survival mode
2. Left-click a block
3. **Expected:** The block is NOT broken, event is cancelled, corner 1 is set

## Test 7: Non-Wand Axe Ignored
1. Hold a regular wooden axe (no custom name)
2. Click a block
3. **Expected:** Normal behavior, no corner messages

## Test 8: No Permission
1. Remove `buildinglore.use` from yourself (deop or use a permission plugin)
2. Hold the wand and click
3. **Expected:** No corner messages, no interaction
