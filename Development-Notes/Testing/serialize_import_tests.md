# Serialize & Import Tests

## Test 1: Serialize a Selection
1. Create a selection with one or more regions
2. Run `/bl serialize myhouse`
3. **Expected:** A token like `[BL:world|10,64,20>25,80,35]` appears in chat
4. Verify the world name, coordinates match what you set

## Test 2: Serialize Multi-Region Selection
1. Create a selection with 2+ regions
2. Run `/bl serialize myhouse`
3. **Expected:** Token contains multiple `|` separated region entries, e.g. `[BL:world|...|...]`

## Test 3: Import a Token
1. Copy the token from the serialize test
2. Run `/bl import [BL:world|10,64,20>25,80,35]`
3. **Expected:** Success message showing region count and world
4. Run `/bl list` — a selection named "imported" should appear
5. Run `/bl info imported` — coordinates should match the original

## Test 4: Import Invalid Token
1. Run `/bl import notavalidtoken`
2. **Expected:** Error message about invalid token format

## Test 5: Import Malformed Coordinates
1. Run `/bl import [BL:world|abc,def,ghi>1,2,3]`
2. **Expected:** Error message (NumberFormatException caught gracefully)

## Test 6: Round-Trip Integrity
1. Create a selection, serialize it
2. Import the token on the same or different account
3. Run `/bl info` on both the original and imported
4. **Expected:** Coordinates and volumes match exactly
