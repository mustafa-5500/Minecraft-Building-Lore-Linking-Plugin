# BuildingLoreCommand.java
[[BuildingLoreCommand.java]]

The command handler for the `/bl` command tree. Implements `TabExecutor` to handle both command execution and tab completion. Routes subcommands to individual handler methods for wand management, selection manipulation, serialization, export/import, and visualization toggling.

**Fields:**
- `plugin` — Reference to the owning `JavaPlugin` instance
- `selectionManager` — Manages per-player ephemeral corner selections
- `storageManager` — Handles persistent selection storage
- `visualizer` — Controls particle-based selection visualization
- `PREFIX` — Chat message prefix for consistent formatting

**Functions:**
[[onCommand]]
[[handleWand]]
[[handlePos]]
[[handleAdd]]
[[handleRemove]]
[[handleList]]
[[handleInfo]]
[[handleDelete]]
[[handleSerialize]]
[[handleExport]]
[[handleImport]]
[[showPreview]]
[[sendHelp]]
[[onTabComplete]]

---

## onCommand

### Signature
```java
@Override
public boolean onCommand(CommandSender sender, Command command, String label, String[] args)
```

### Description
Entry point for the `/bl` command. Ensures the sender is a player, then dispatches to the appropriate subcommand handler based on `args[0]`. Shows help if no arguments or unknown subcommand.

### Subcommands Dispatched
`wand`, `pos1`, `pos2`, `add`, `remove`, `list`, `info`, `delete`, `serialize`, `export`, `import`

### Returns
`boolean` — always `true` (command was handled).

---

## handleWand

### Signature
```java
private void handleWand(Player player)
```

### Description
Gives the player a selection wand item. Requires `buildinglore.use` permission.

---

## handlePos1 / handlePos2

### Signatures
```java
private void handlePos1(Player player)
private void handlePos2(Player player)
```

### Description
Sets corner 1 or corner 2 to the player's current standing position (alternative to wand clicks). Shows a selection preview if both corners are now set. Requires `buildinglore.use` permission.

---

## handleAdd

### Signature
```java
private void handleAdd(Player player, String[] args)
```

### Description
Builds a `CuboidRegion` from the player's current corners and adds it to the named selection. Creates the selection if it doesn't exist. Saves to disk immediately.

### Usage
`/bl add <name>`

### Requires
- Both corners set
- `buildinglore.use` permission

---

## handleRemove

### Signature
```java
private void handleRemove(Player player, String[] args)
```

### Description
Removes a region from a named selection by its 0-based index. Saves the updated selection to disk.

### Usage
`/bl remove <name> <index>`

### Requires
- `buildinglore.use` permission

---

## handleList

### Signature
```java
private void handleList(Player player)
```

### Description
Lists all of the player's saved selections, showing name, region count, total volume, and world name.

### Usage
`/bl list`

### Requires
- `buildinglore.use` permission

---

## handleInfo

### Signature
```java
private void handleInfo(Player player, String[] args)
```

### Description
Displays detailed information about a named selection: world, total volume, and each region with its index, coordinates, and individual volume.

### Usage
`/bl info <name>`

### Requires
- `buildinglore.use` permission

---

## handleDelete

### Signature
```java
private void handleDelete(Player player, String[] args)
```

### Description
Deletes a named selection from disk and cache.

### Usage
`/bl delete <name>`

### Requires
- `buildinglore.use` permission

---

## handleSerialize

### Signature
```java
private void handleSerialize(Player player, String[] args)
```

### Description
Outputs the compact `[BL:...]` text token for a named selection. The token can be copy-pasted into documents and later imported.

### Usage
`/bl serialize <name>`

### Requires
- `buildinglore.use` permission

---

## handleExport

### Signature
```java
private void handleExport(Player player, String[] args)
```

### Description
Exports block data for a named selection to a text file at `plugins/BuildingLore/exports/<uuid>/<name>.txt`. Reads blocks synchronously from the world. Skips air blocks.

### Usage
`/bl export <name>`

### Requires
- `buildinglore.export` permission (op by default)

---

## handleImport

### Signature
```java
private void handleImport(Player player, String[] args)
```

### Description
Parses a `[BL:...]` text token and creates a new selection from it, saved as "imported". Rejoins args to handle any accidental spaces in the token.

### Usage
`/bl import <token>`

### Requires
- `buildinglore.use` permission

---

## showPreview

### Signature
```java
private void showPreview(Player player)
```

### Description
If the player has a complete selection (both corners set), shows the region coordinates and volume as a chat message.

---

## sendHelp

### Signature
```java
private void sendHelp(Player player)
```

### Description
Displays a formatted help message listing all available `/bl` subcommands and their descriptions.

---

## onTabComplete

### Signature
```java
@Override
public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args)
```

### Description
Provides tab completion suggestions. For the first argument, suggests all subcommand names. For the second argument on subcommands that take a selection name, suggests the player's existing selection names.

### Returns
`List<String>` — filtered suggestions matching the partial input.
