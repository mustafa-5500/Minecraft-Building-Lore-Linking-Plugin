# Persistence & Edge Case Tests

## Test 1: Selections Survive Server Restart
1. Create a selection with `/bl add myhouse`
2. Restart the server
3. Run `/bl list` and `/bl info myhouse`
4. **Expected:** Selection is fully intact with correct regions, volume, world

## Test 2: Multiple Players Independent
1. Have two players each create selections with the same name (e.g. both use "test")
2. Each runs `/bl list`
3. **Expected:** Each player only sees their own selection. Files stored under separate UUID folders.

## Test 3: Cross-World Prevention
1. Set corner 1 in the overworld
2. Travel to the nether, set corner 2
3. Run `/bl add test`
4. **Expected:** Error — corners must be in the same world

## Test 4: Selection Name With Spaces
1. Run `/bl add my house`
2. **Expected:** Only "my" is used as the name (args[1]). Consider whether this is acceptable or needs quoting support.

## Test 5: Empty Selection After Removing All Regions
1. Create a selection with 1 region
2. Remove it with `/bl remove test 0`
3. Run `/bl info test`
4. **Expected:** Shows 0 regions, 0 volume. No crash.

## Test 6: Console Sender Rejected
1. From the server console, run `bl list`
2. **Expected:** "This command can only be used by players." message

## Test 7: Help Command
1. Run `/bl` with no arguments
2. Run `/bl unknowncommand`
3. **Expected:** Both show the help message listing all subcommands

## Test 8: YAML File Integrity
1. Create a selection, then open its `.yml` file manually
2. **Expected:** Contains id, name, owner, world, createdAt, and regions as a list of coordinate strings
3. Edit a coordinate in the file, restart server, load the selection
4. **Expected:** The edit is reflected correctly

## Test 9: Corrupt YAML Handling
1. Manually corrupt a selection `.yml` file (delete a field, add invalid YAML)
2. Restart server and run `/bl list`
3. **Expected:** The corrupt file is skipped with a warning in the server log, other selections load fine
