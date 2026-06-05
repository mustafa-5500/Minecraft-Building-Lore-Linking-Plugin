# BuildingLorePlugin — Software Detailed Design

> **API Documentation:** [BuildingLorePlugin.md](./BuildingLorePlugin.md)  
> **Source File:** [BuildingLorePlugin.java](../src/main/java/org/almond/buildinglore/BuildingLorePlugin.java)

---

## 1. Overview

`BuildingLorePlugin` is the main entry point class for the BuildingLore Bukkit/Paper plugin. It extends `JavaPlugin`, making it the lifecycle owner that the server instantiates when the plugin JAR is loaded. This class is responsible for initializing all subsystems (managers, visualizers), registering event listeners, binding the command executor, and performing cleanup on shutdown.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore;
```
Declares this class in the root plugin package.

```java
import org.almond.buildinglore.command.BuildingLoreCommand;
import org.almond.buildinglore.listener.LoreChatListener;
import org.almond.buildinglore.listener.WandListener;
import org.almond.buildinglore.manager.LoreDocumentManager;
import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.manager.SelectionStorageManager;
import org.almond.buildinglore.visual.SelectionVisualizer;
import org.bukkit.command.PluginCommand;
import org.bukkit.plugin.java.JavaPlugin;
```

| Import | Purpose |
|--------|---------|
| [`BuildingLoreCommand`](command/BuildingLoreCommand.md) | The `/bl` command executor and tab completer |
| [`LoreChatListener`](listener/LoreChatListener.md) | Event listener that captures chat input during lore editing sessions |
| [`WandListener`](listener/WandListener.md) | Event listener that handles wand click interactions for corner selection |
| [`LoreDocumentManager`](manager/LoreDocumentManager.md) | Manages per-player lore document input state |
| [`SelectionManager`](manager/SelectionManager.md) | Manages per-player ephemeral wand corner state in memory |
| [`SelectionStorageManager`](manager/SelectionStorageManager.md) | Handles disk persistence (YAML) of selections |
| [`SelectionVisualizer`](visual/SelectionVisualizer.md) | Draws particle outlines of selections |
| `PluginCommand` | Bukkit API class representing a registered command |
| `JavaPlugin` | Bukkit base class for all plugins |

---

## 3. Class Declaration

```java
public class BuildingLorePlugin extends JavaPlugin {
```

- **`public`** — accessible by the server's plugin loader.
- **`extends JavaPlugin`** — inherits Bukkit plugin lifecycle methods (`onEnable`, `onDisable`), configuration access, logger, data folder, and command registration.

---

## 4. Instance Fields

```java
private SelectionManager selectionManager;
private SelectionStorageManager storageManager;
private SelectionVisualizer visualizer;
private LoreDocumentManager loreManager;
```

| Field | Type | Responsibility |
|-------|------|----------------|
| `selectionManager` | [`SelectionManager`](manager/SelectionManager.md) | In-memory map of player UUID → corner 1/corner 2 locations |
| `storageManager` | [`SelectionStorageManager`](manager/SelectionStorageManager.md) | Reads/writes [`Selection`](model/Selection.md) objects as YAML under the plugin data folder |
| `visualizer` | [`SelectionVisualizer`](visual/SelectionVisualizer.md) | Schedules particle rendering tasks showing cuboid edges |
| `loreManager` | [`LoreDocumentManager`](manager/LoreDocumentManager.md) | Tracks which players are currently in lore naming/writing chat mode |

All fields are `private` and not exposed via setters — they are initialized exactly once in `onEnable` and accessed via getters.

---

## 5. `onEnable()`

```java
@Override
public void onEnable() {
```
Called by the Bukkit server when the plugin transitions to the **enabled** state (during server startup or a `/reload`).

### 5.1 Manager Initialization

```java
    selectionManager = new SelectionManager();
```
Creates the ephemeral per-player corner map. No arguments needed — it starts as an empty `HashMap`.

```java
    storageManager = new SelectionStorageManager(this);
```
Creates the persistent storage manager. Passing `this` (the `JavaPlugin` instance) allows it to resolve `getDataFolder()` for file paths and use the plugin logger.

```java
    visualizer = new SelectionVisualizer(this, selectionManager);
```
Creates the visualizer, which needs both the plugin reference (for scheduling Bukkit tasks) and the selection manager (to read current corner data each render tick).

```java
    loreManager = new LoreDocumentManager();
```
Creates the lore input state manager. Starts with an empty pending-input map.

### 5.2 Listener Registration

```java
    getServer().getPluginManager().registerEvents(new WandListener(selectionManager, visualizer), this);
```
- `getServer().getPluginManager()` — accesses the Bukkit `PluginManager` singleton.
- `registerEvents(...)` — scans the listener instance for `@EventHandler` methods and subscribes them.
- `new WandListener(selectionManager, visualizer)` — the listener needs the selection manager to record corners and the visualizer to auto-enable particles.
- `this` — identifies this plugin as the event owner (used for unregistration on disable).

```java
    getServer().getPluginManager().registerEvents(new LoreChatListener(loreManager, storageManager), this);
```
Registers the chat listener that intercepts messages from players in lore input mode. Needs `loreManager` to check/clear input state and `storageManager` to persist document changes.

### 5.3 Command Registration

```java
    BuildingLoreCommand cmdExecutor = new BuildingLoreCommand(this, selectionManager, storageManager, visualizer, loreManager);
```
Constructs the command handler with all five dependencies injected.

```java
    PluginCommand blCommand = getCommand("bl");
```
Retrieves the `PluginCommand` registered in `plugin.yml` under the name `bl`. Returns `null` if not declared.

```java
    if (blCommand != null) {
        blCommand.setExecutor(cmdExecutor);
        blCommand.setTabCompleter(cmdExecutor);
    }
```
- Null-check guards against misconfigured `plugin.yml`.
- `setExecutor` — routes `/bl ...` invocations to `cmdExecutor.onCommand(...)`.
- `setTabCompleter` — routes tab-completion requests to `cmdExecutor.onTabComplete(...)`.

### 5.4 Startup Log

```java
    getLogger().info("BuildingLore enabled.");
}
```
Prints a confirmation message to the server console using the plugin's prefixed logger.

---

## 6. `onDisable()`

```java
@Override
public void onDisable() {
    visualizer.shutdown();
    getLogger().info("BuildingLore disabled.");
}
```

- **`visualizer.shutdown()`** — cancels the repeating particle task and clears the enabled-player set. This prevents orphaned scheduler tasks after reload.
- Logs a shutdown message. Other managers (`selectionManager`, `storageManager`, `loreManager`) hold no resources requiring explicit cleanup — they are purely in-memory maps that will be garbage-collected.

---

## 7. Getter Methods

```java
public SelectionManager getSelectionManager() {
    return selectionManager;
}
```
Provides external access to the selection manager (e.g., for other plugins integrating with BuildingLore).

```java
public SelectionStorageManager getStorageManager() {
    return storageManager;
}
```
Exposes the storage manager for external persistence operations.

```java
public SelectionVisualizer getVisualizer() {
    return visualizer;
}
```
Exposes the visualizer for external toggle/query.

```java
public LoreDocumentManager getLoreManager() {
    return loreManager;
}
```
Exposes the lore document manager for external state queries.

---

## 8. Lifecycle & Dependency Flow

```
Server starts
  └─► onEnable()
        ├─► SelectionManager (new)
        ├─► SelectionStorageManager (new, depends on plugin data folder)
        ├─► SelectionVisualizer (new, depends on plugin + SelectionManager)
        ├─► LoreDocumentManager (new)
        ├─► WandListener registered (depends on SelectionManager + Visualizer)
        ├─► LoreChatListener registered (depends on LoreDocumentManager + StorageManager)
        └─► BuildingLoreCommand bound (depends on all managers + Visualizer)

Server stops / plugin reload
  └─► onDisable()
        └─► visualizer.shutdown() — cancels scheduled task
```

---

## 9. Design Decisions

| Decision | Rationale |
|----------|-----------|
| All managers created in `onEnable` (not constructor) | Bukkit plugins must not perform initialization in the constructor; server APIs are unavailable until `onEnable`. |
| Dependency injection via constructor arguments | Avoids static singletons, making components testable in isolation. |
| Single command executor for `/bl` | Centralizes subcommand routing in one `TabExecutor` implementation rather than splitting across multiple classes. |
| `visualizer.shutdown()` in `onDisable` | The visualizer owns a `BukkitTask`; failing to cancel it causes `IllegalPluginAccessException` after reload. |
| No explicit `storageManager` shutdown | YAML files are written synchronously on each save; no buffered writes to flush. |
