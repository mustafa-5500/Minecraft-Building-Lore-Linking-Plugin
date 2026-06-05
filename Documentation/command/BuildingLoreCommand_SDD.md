# BuildingLoreCommand — Software Detailed Design

> **API Documentation:** [BuildingLoreCommand.md](./BuildingLoreCommand.md)  
> **Source File:** [BuildingLoreCommand.java](../../src/main/java/org/almond/buildinglore/command/BuildingLoreCommand.java)

---

## 1. Overview

`BuildingLoreCommand` implements the entire `/bl` command tree. It serves as both the command executor (`onCommand`) and tab completer (`onTabComplete`) via the `TabExecutor` interface. The class routes subcommands to private handler methods and delegates business logic to injected manager dependencies.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.command;
```

```java
import org.almond.buildinglore.manager.LoreDocumentManager;
import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.manager.SelectionStorageManager;
import org.almond.buildinglore.model.CuboidRegion;
import org.almond.buildinglore.model.LoreDocument;
import org.almond.buildinglore.model.Selection;
import org.almond.buildinglore.serializer.BlockDataExporter;
import org.almond.buildinglore.serializer.RegionSerializer;
import org.almond.buildinglore.util.WandUtil;
import org.almond.buildinglore.visual.SelectionVisualizer;
import org.bukkit.ChatColor;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabExecutor;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
```

| Import Category | Items | Purpose |
|-----------------|-------|---------|
| Plugin managers | [`LoreDocumentManager`](../manager/LoreDocumentManager.md), [`SelectionManager`](../manager/SelectionManager.md), [`SelectionStorageManager`](../manager/SelectionStorageManager.md) | Business logic delegation |
| Models | [`CuboidRegion`](../model/CuboidRegion.md), [`LoreDocument`](../model/LoreDocument.md), [`Selection`](../model/Selection.md) | Data structures passed between layers |
| Serializers | [`BlockDataExporter`](../serializer/BlockDataExporter.md), [`RegionSerializer`](../serializer/RegionSerializer.md) | Export/import operations |
| Utility | [`WandUtil`](../util/WandUtil.md) | Wand item creation |
| Visual | [`SelectionVisualizer`](../visual/SelectionVisualizer.md) | Particle toggle |
| Bukkit API | `ChatColor`, `World`, `Command`, `CommandSender`, `TabExecutor`, `Player`, `JavaPlugin` | Server interaction |
| Java standard | `File`, `ArrayList`, `Collections`, `List`, `Collectors` | I/O and collection manipulation |

---

## 3. Class Declaration

```java
public class BuildingLoreCommand implements TabExecutor {
```

`TabExecutor` is a Bukkit interface combining `CommandExecutor` (handles execution) and `TabCompleter` (handles tab suggestions). Implementing both in one class keeps the command's logic collocated.

---

## 4. Instance Fields

```java
private final JavaPlugin plugin;
private final SelectionManager selectionManager;
private final SelectionStorageManager storageManager;
private final SelectionVisualizer visualizer;
private final LoreDocumentManager loreManager;
```

All fields are `final` — set once in the constructor and never reassigned.

| Field | Usage |
|-------|-------|
| `plugin` | Access to `getDataFolder()`, `getServer()`, `getLogger()` for export operations |
| `selectionManager` | Read/write wand corner state |
| `storageManager` | CRUD operations on persistent selections |
| `visualizer` | Toggle particle rendering |
| `loreManager` | Start lore naming/writing input flow |

```java
private static final String PREFIX = ChatColor.DARK_AQUA + "[BuildingLore] " + ChatColor.RESET;
```

A compile-time constant string prepended to all player messages for consistent branding. `ChatColor.RESET` ensures subsequent text uses default color.

---

## 5. Constructor

```java
public BuildingLoreCommand(JavaPlugin plugin, SelectionManager selectionManager, SelectionStorageManager storageManager, SelectionVisualizer visualizer, LoreDocumentManager loreManager) {
    this.plugin = plugin;
    this.selectionManager = selectionManager;
    this.storageManager = storageManager;
    this.visualizer = visualizer;
    this.loreManager = loreManager;
}
```

Pure dependency injection — no side effects. All five collaborators are required for the command to function.

---

## 6. `onCommand()`

```java
@Override
public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
```

Bukkit calls this when a player (or console) executes `/bl [args...]`.

### 6.1 Player-Only Guard

```java
    if (!(sender instanceof Player player)) {
        sender.sendMessage("This command can only be used by players.");
        return true;
    }
```

Uses Java 16+ pattern matching for `instanceof`. If the sender is not a `Player` (e.g., console), the command is rejected. Returning `true` tells Bukkit the command was handled (suppresses the usage message from `plugin.yml`).

### 6.2 No-Arguments: Show Help

```java
    if (args.length == 0) {
        sendHelp(player);
        return true;
    }
```

If the player types bare `/bl`, display the help listing.

### 6.3 Subcommand Routing

```java
    String sub = args[0].toLowerCase();

    switch (sub) {
        case "wand" -> handleWand(player);
        case "pos1" -> handlePos1(player);
        case "pos2" -> handlePos2(player);
        case "add" -> handleAdd(player, args);
        case "remove" -> handleRemove(player, args);
        case "list" -> handleList(player);
        case "info" -> handleInfo(player, args);
        case "delete" -> handleDelete(player, args);
        case "serialize" -> handleSerialize(player, args);
        case "export" -> handleExport(player, args);
        case "import" -> handleImport(player, args);
        case "viz" -> handleViz(player);
        case "lore" -> handleLore(player, args);
        default -> sendHelp(player);
    }
    return true;
```

- `args[0]` is lowercased for case-insensitive matching.
- Java 14+ switch expressions with `->` arrows (no fall-through).
- Unknown subcommands trigger the help display.
- Always returns `true` — command is always considered handled.

---

## 7. Subcommand Handlers

### 7.1 `handleWand(Player)`

```java
private void handleWand(Player player) {
    if (!player.hasPermission("buildinglore.use")) {
        player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
        return;
    }
    player.getInventory().addItem(WandUtil.createWand());
    player.sendMessage(PREFIX + "Selection wand given. Left-click to set corner 1, right-click for corner 2.");
}
```

1. Permission check: `buildinglore.use`.
2. `WandUtil.createWand()` creates a `WOODEN_AXE` with custom display name and lore.
3. `addItem(...)` places it in the first available inventory slot (or drops it if full).
4. Confirmation message with usage instructions.

### 7.2 `handlePos1(Player)` / `handlePos2(Player)`

```java
private void handlePos1(Player player) {
    if (!player.hasPermission("buildinglore.use")) { ... }
    selectionManager.setCorner1(player.getUniqueId(), player.getLocation());
    player.sendMessage(PREFIX + ChatColor.YELLOW + "Corner 1 set to your position.");
    showPreview(player);
}
```

- Uses `player.getLocation()` (feet position) as the corner.
- Delegates to `selectionManager.setCorner1(UUID, Location)` which stores it in a `HashMap`.
- Calls `showPreview` to display the cuboid dimensions if both corners are set.

`handlePos2` is identical except it calls `setCorner2`.

### 7.3 `handleAdd(Player, String[])`

```java
private void handleAdd(Player player, String[] args) {
    if (!player.hasPermission("buildinglore.use")) { ... }
    if (args.length < 2) {
        player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl add <name>");
        return;
    }
    if (!selectionManager.hasCompleteSelection(player.getUniqueId())) {
        player.sendMessage(PREFIX + ChatColor.RED + "Set both corners first (wand or /bl pos1 & /bl pos2).");
        return;
    }

    String name = args[1];
    CuboidRegion region = selectionManager.buildRegion(player.getUniqueId());
    if (region == null) {
        player.sendMessage(PREFIX + ChatColor.RED + "Failed to create region.");
        return;
    }

    Selection selection = storageManager.getSelection(player.getUniqueId(), name);
    if (selection == null) {
        selection = new Selection(name, player.getUniqueId(), region.getWorldName());
    }
    selection.addRegion(region);
    storageManager.saveSelection(selection);

    player.sendMessage(PREFIX + "Region added to " + ChatColor.GREEN + name +
        ChatColor.RESET + ". Total regions: " + selection.getRegionCount() +
        ", Volume: " + selection.getTotalVolume() + " blocks.");
}
```

**Flow:**
1. Validate permissions and argument count.
2. Verify both corners exist and share the same world (`hasCompleteSelection`).
3. `buildRegion` constructs a [`CuboidRegion`](../model/CuboidRegion.md) from the two corners and **clears** them from memory.
4. Load existing selection by name, or create a new one.
5. `addRegion` handles overlap resolution (subtraction, merging).
6. Persist to disk.
7. Report the updated selection stats to the player.

### 7.4 `handleRemove(Player, String[])`

```java
private void handleRemove(Player player, String[] args) {
    if (!player.hasPermission("buildinglore.use")) { ... }
    if (args.length < 3) {
        player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl remove <name> <index>");
        return;
    }
    String name = args[1];
    int index;
    try {
        index = Integer.parseInt(args[2]);
    } catch (NumberFormatException e) {
        player.sendMessage(PREFIX + ChatColor.RED + "Index must be a number.");
        return;
    }

    Selection selection = storageManager.getSelection(player.getUniqueId(), name);
    if (selection == null) { ... }
    if (!selection.removeRegion(index)) {
        player.sendMessage(PREFIX + ChatColor.RED + "Invalid region index. Use /bl info " + name + " to see indices.");
        return;
    }
    storageManager.saveSelection(selection);
    player.sendMessage(PREFIX + "Region " + index + " removed from " + ChatColor.GREEN + name + ChatColor.RESET + ".");
}
```

- Parses the index with `Integer.parseInt`, catching `NumberFormatException`.
- `removeRegion(index)` returns `false` if out of bounds.
- Persists after modification.

### 7.5 `handleList(Player)`

```java
private void handleList(Player player) {
    if (!player.hasPermission("buildinglore.use")) { ... }
    List<Selection> selections = storageManager.loadAllForPlayer(player.getUniqueId());
    if (selections.isEmpty()) {
        player.sendMessage(PREFIX + "You have no saved selections.");
        return;
    }
    player.sendMessage(PREFIX + ChatColor.AQUA + "Your Selections:");
    for (Selection sel : selections) {
        player.sendMessage(ChatColor.GREEN + "  " + sel.getName() +
            ChatColor.GRAY + " — " + sel.getRegionCount() + " regions, " +
            sel.getTotalVolume() + " blocks (" + sel.getWorldName() + ")");
    }
}
```

Loads all YAML files for the player and displays a summary line for each.

### 7.6 `handleInfo(Player, String[])`

```java
private void handleInfo(Player player, String[] args) {
    ...
    Selection selection = storageManager.getSelection(player.getUniqueId(), name);
    ...
    player.sendMessage(PREFIX + ChatColor.AQUA + "Selection: " + ChatColor.GREEN + selection.getName());
    player.sendMessage(ChatColor.GRAY + "  World: " + selection.getWorldName());
    player.sendMessage(ChatColor.GRAY + "  Total Volume: " + selection.getTotalVolume() + " blocks");
    player.sendMessage(ChatColor.GRAY + "  Regions (" + selection.getRegionCount() + "):");
    List<CuboidRegion> regions = selection.getRegions();
    for (int i = 0; i < regions.size(); i++) {
        CuboidRegion r = regions.get(i);
        player.sendMessage(ChatColor.WHITE + "    [" + i + "] " + r.toString() + ChatColor.GRAY + " (" + r.getVolume() + " blocks)");
    }
}
```

Prints detailed metadata including every region with its 0-based index, coordinate range, and volume.

### 7.7 `handleDelete(Player, String[])`

```java
private void handleDelete(Player player, String[] args) {
    ...
    if (storageManager.deleteSelection(player.getUniqueId(), name)) {
        player.sendMessage(PREFIX + "Selection " + ChatColor.GREEN + name + ChatColor.RESET + " deleted.");
    } else {
        player.sendMessage(PREFIX + ChatColor.RED + "Selection '" + name + "' not found.");
    }
}
```

Delegates to `storageManager.deleteSelection` which removes both the file and cache entry.

### 7.8 `handleSerialize(Player, String[])`

```java
private void handleSerialize(Player player, String[] args) {
    ...
    String token = RegionSerializer.serialize(selection);
    player.sendMessage(PREFIX + "Serialized token:");
    player.sendMessage(ChatColor.WHITE + token);
}
```

Produces a compact `[BL:world|x,y,z>x,y,z|...]` token the player can copy-paste.

### 7.9 `handleExport(Player, String[])`

```java
private void handleExport(Player player, String[] args) {
    if (!player.hasPermission("buildinglore.export")) { ... }
    ...
    World world = plugin.getServer().getWorld(selection.getWorldName());
    if (world == null) { ... }

    player.sendMessage(PREFIX + "Exporting block data for '" + name + "'... (this may take a moment)");

    try {
        File exportDir = new File(plugin.getDataFolder(), "exports" + File.separator + player.getUniqueId());
        File outputFile = BlockDataExporter.exportToFile(selection, world, exportDir, true);
        player.sendMessage(PREFIX + ChatColor.GREEN + "Exported to: " + outputFile.getPath());
    } catch (Exception e) {
        player.sendMessage(PREFIX + ChatColor.RED + "Export failed: " + e.getMessage());
        plugin.getLogger().warning("Export failed for " + name + ": " + e.getMessage());
    }
}
```

- Requires elevated permission `buildinglore.export`.
- Resolves the Bukkit `World` by name.
- Creates a player-specific export directory under `plugins/BuildingLore/exports/<uuid>/`.
- `exportToFile` reads block data **synchronously on the main thread** (required by Bukkit API) and writes a `.txt` file.
- Exception handling reports to both the player and server log.

### 7.10 `handleImport(Player, String[])`

```java
private void handleImport(Player player, String[] args) {
    ...
    String token = String.join(" ", java.util.Arrays.copyOfRange(args, 1, args.length));
    try {
        Selection selection = RegionSerializer.deserialize(token, player.getUniqueId());
        storageManager.saveSelection(selection);
        player.sendMessage(PREFIX + "Imported selection with " + selection.getRegionCount() +
            " regions in world '" + selection.getWorldName() + "'.");
        ...
    } catch (IllegalArgumentException e) {
        player.sendMessage(PREFIX + ChatColor.RED + "Invalid token: " + e.getMessage());
    }
}
```

- Rejoins args 1..n in case the token contained spaces (defensive).
- `RegionSerializer.deserialize` parses the compact token format.
- The resulting selection is named `"imported"` and saved with a new random UUID.
- Catches `IllegalArgumentException` for malformed tokens.

### 7.11 `handleLore(Player, String[])`

```java
private void handleLore(Player player, String[] args) {
    ...
    String action = args[1].toLowerCase();
    String selectionName = args[2];

    Selection selection = storageManager.getSelection(player.getUniqueId(), selectionName);
    if (selection == null) { ... }

    switch (action) {
        case "add" -> { ... loreManager.startNaming(player.getUniqueId(), selectionName); ... }
        case "write" -> { ... loreManager.startWriting(player.getUniqueId(), selectionName, docName); ... }
        case "list" -> { ... iterate docs and print ... }
        case "read" -> { ... print all entries ... }
        case "delete" -> { ... selection.removeLoreDocument(docName); storageManager.saveSelection(selection); ... }
        default -> sendLoreHelp(player);
    }
}
```

A nested subcommand tree under `/bl lore`. Actions:
- **`add`** — initiates chat-based naming flow via [`LoreDocumentManager`](../manager/LoreDocumentManager.md).
- **`write`** — initiates chat-based text entry flow.
- **`list`** — displays all lore documents in a selection.
- **`read`** — displays all entries in a specific document.
- **`delete`** — removes a document from the selection and saves.

### 7.12 `handleViz(Player)`

```java
private void handleViz(Player player) {
    ...
    boolean nowEnabled = visualizer.toggle(player.getUniqueId());
    if (nowEnabled) {
        player.sendMessage(PREFIX + ChatColor.GREEN + "Selection visualization enabled.");
    } else {
        player.sendMessage(PREFIX + ChatColor.YELLOW + "Selection visualization disabled.");
    }
}
```

Toggles particle rendering for the player and reports the new state.

---

## 8. Helper Methods

### 8.1 `showPreview(Player)`

```java
private void showPreview(Player player) {
    if (selectionManager.hasCompleteSelection(player.getUniqueId())) {
        CuboidRegion preview = selectionManager.peekRegion(player.getUniqueId());
        if (preview != null) {
            player.sendMessage(PREFIX + ChatColor.GRAY + "Selection: " + preview.toString() +
                " (" + preview.getVolume() + " blocks)");
        }
    }
}
```

Called after `pos1`/`pos2` to show immediate feedback. `peekRegion` reads without consuming the corners.

### 8.2 `sendHelp(Player)` / `sendLoreHelp(Player)`

Multi-line help messages listing all subcommands with brief descriptions. Uses `ChatColor.YELLOW` for command syntax and `ChatColor.GRAY` for descriptions.

---

## 9. Tab Completion — `onTabComplete()`

```java
@Override
public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
    if (!(sender instanceof Player player)) return Collections.emptyList();
```

Only provides suggestions for players.

### 9.1 First Argument — Subcommand Names

```java
    if (args.length == 1) {
        List<String> subs = List.of("wand", "pos1", "pos2", "add", "remove", "list", "info", "delete", "serialize", "export", "import", "viz", "lore");
        return subs.stream()
            .filter(s -> s.startsWith(args[0].toLowerCase()))
            .collect(Collectors.toList());
    }
```

Filters the full subcommand list by the partially-typed prefix.

### 9.2 Second Argument — Context-Sensitive

```java
    if (args.length == 2) {
        String sub = args[0].toLowerCase();
        if (sub.equals("lore")) {
            // Suggest lore actions: add, write, list, read, delete
            ...
        }
        if (List.of("add", "remove", "info", "delete", "serialize", "export").contains(sub)) {
            // Suggest player's selection names from storage
            return storageManager.loadAllForPlayer(player.getUniqueId()).stream()
                .map(Selection::getName)
                .filter(n -> n.toLowerCase().startsWith(args[1].toLowerCase()))
                .collect(Collectors.toList());
        }
    }
```

### 9.3 Third Argument — Selection Names for Lore

```java
    if (args.length == 3 && sub.equals("lore")) {
        // Suggest selection names
    }
```

### 9.4 Fourth Argument — Lore Document Names

```java
    if (args.length == 4 && sub.equals("lore") && List.of("write", "read", "delete").contains(loreAction)) {
        Selection sel = storageManager.getSelection(player.getUniqueId(), selName);
        if (sel != null) {
            return sel.getLoreDocuments().keySet().stream()...
        }
    }
```

Falls through to `Collections.emptyList()` for all other cases.

---

## 10. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single class for all subcommands | Keeps routing visible; avoids class explosion for a moderate command tree. |
| Permission checks at the start of each handler | Early-exit pattern prevents any logic from executing without permission. |
| `return true` always | All validation/error messages are handled internally; Bukkit's default usage message is never shown. |
| Tab completion loads from storage | Gives live feedback as selections are created/deleted. |
| Synchronous export on main thread | Bukkit's `World.getBlockAt()` is not thread-safe; a future improvement could chunk work across ticks. |

## 11. `handlePos2()`

```java
private void handlePos2(Player player)
```

TODO: Provide detailed design explanation for `handlePos2`.

---

## 12. `sendLoreHelp()`

```java
private void sendLoreHelp(Player player)
```

TODO: Provide detailed design explanation for `sendLoreHelp`.

---

## 13. `sendHelp()`

```java
private void sendHelp(Player player)
```

TODO: Provide detailed design explanation for `sendHelp`.

---
