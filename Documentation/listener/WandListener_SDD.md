# WandListener — Software Detailed Design

> **API Documentation:** [WandListener.md](./WandListener.md)  
> **Source File:** [WandListener.java](../../src/main/java/org/almond/buildinglore/listener/WandListener.java)

---

## 1. Overview

`WandListener` is a Bukkit event listener that intercepts player block-interaction events (`PlayerInteractEvent`) and, if the player is holding the BuildingLore selection wand, records the clicked block as either corner 1 (left-click) or corner 2 (right-click) of their selection. It also provides immediate volume feedback and auto-enables the particle visualizer.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.listener;
```

```java
import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.visual.SelectionVisualizer;
import org.almond.buildinglore.util.WandUtil;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.player.PlayerInteractEvent;
```

| Import | Purpose |
|--------|---------|
| [`SelectionManager`](../manager/SelectionManager.md) | Store the clicked block position as corner 1 or 2 |
| [`SelectionVisualizer`](../visual/SelectionVisualizer.md) | Auto-enable particle preview on first wand use |
| [`WandUtil`](../util/WandUtil.md) | Identify whether the held item is the selection wand |
| `ChatColor` | Colored chat messages |
| `Location` | Represents a 3D position in a world |
| `Block` | The block that was clicked |
| `Player` | The interacting player |
| `EventHandler` | Annotation marking this method as an event subscriber |
| `Listener` | Marker interface required for Bukkit event registration |
| `Action` | Enum: `LEFT_CLICK_BLOCK`, `RIGHT_CLICK_BLOCK`, etc. |
| `PlayerInteractEvent` | Fired when a player interacts with or clicks on a block |

---

## 3. Class Declaration

```java
public class WandListener implements Listener {
```

Implementing `Listener` is required for Bukkit's `PluginManager.registerEvents(...)` to recognize this class as an event subscriber.

---

## 4. Instance Fields

```java
private final SelectionManager selectionManager;
private final SelectionVisualizer visualizer;
```

Both are injected via the constructor and held as `final` references.

---

## 5. Constructor

```java
public WandListener(SelectionManager selectionManager, SelectionVisualizer visualizer) {
    this.selectionManager = selectionManager;
    this.visualizer = visualizer;
}
```

Simple dependency injection. This listener is instantiated in `BuildingLorePlugin.onEnable()`.

---

## 6. Event Handler: `onPlayerInteract`

```java
@EventHandler
public void onPlayerInteract(PlayerInteractEvent event) {
```

`@EventHandler` with default priority (`NORMAL`). Bukkit will invoke this method whenever any player interacts with anything (click, use item, etc.).

### 6.1 Get the Player

```java
    Player player = event.getPlayer();
```

Extracts the `Player` who triggered the event.

### 6.2 Wand Check

```java
    if (!WandUtil.isWand(player.getInventory().getItemInMainHand())) return;
```

- `getItemInMainHand()` — retrieves the item in the player's main hand slot.
- `WandUtil.isWand(ItemStack)` — checks material is `WOODEN_AXE` and display name matches the wand constant.
- Early return if not holding the wand — all non-wand interactions pass through unaffected.

### 6.3 Permission Check

```java
    if (!player.hasPermission("buildinglore.use")) return;
```

Players without the `buildinglore.use` permission node can hold the wand but it won't function. Silent failure (no message) to avoid spam.

### 6.4 Clicked Block Validation

```java
    Block block = event.getClickedBlock();
    if (block == null) return;
```

`getClickedBlock()` returns `null` for air-clicks (e.g., left-clicking air or `LEFT_CLICK_AIR`). We need a physical block to get coordinates.

### 6.5 Extract Location

```java
    Location loc = block.getLocation();
```

Gets the `Location` of the block (integer block coordinates plus world reference).

### 6.6 Corner Assignment Based on Click Type

```java
    if (event.getAction() == Action.LEFT_CLICK_BLOCK) {
        selectionManager.setCorner1(player.getUniqueId(), loc);
        player.sendMessage(ChatColor.YELLOW + "Corner 1 set: " +
            ChatColor.WHITE + loc.getBlockX() + ", " + loc.getBlockY() + ", " + loc.getBlockZ());
        event.setCancelled(true);
    } else if (event.getAction() == Action.RIGHT_CLICK_BLOCK) {
        selectionManager.setCorner2(player.getUniqueId(), loc);
        player.sendMessage(ChatColor.YELLOW + "Corner 2 set: " +
            ChatColor.WHITE + loc.getBlockX() + ", " + loc.getBlockY() + ", " + loc.getBlockZ());
        event.setCancelled(true);
    }
```

- **Left-click** → corner 1.
- **Right-click** → corner 2.
- `event.setCancelled(true)` — prevents the normal click behavior (e.g., breaking the block on left-click, opening a door on right-click).
- Message shows integer coordinates (`getBlockX/Y/Z`).

### 6.7 Volume Preview

```java
    if (selectionManager.hasCompleteSelection(player.getUniqueId())) {
        var preview = selectionManager.peekRegion(player.getUniqueId());
        if (preview != null) {
            player.sendMessage(ChatColor.GRAY + "Selection volume: " + ChatColor.WHITE + preview.getVolume() + " blocks");
        }
    }
```

- Checks if **both** corners are now set and in the same world.
- `peekRegion` constructs a temporary [`CuboidRegion`](../model/CuboidRegion.md) without consuming the corners.
- Displays the total block volume for immediate spatial awareness.

### 6.8 Auto-Enable Visualization

```java
    if (!visualizer.isEnabled(player.getUniqueId())) {
        visualizer.toggle(player.getUniqueId());
    }
```

The first time a player uses the wand, visualization is automatically enabled. If already enabled, this is a no-op. This ensures the player sees the particle outline without needing to run `/bl viz` separately.

---

## 7. Execution Flow Diagram

```
PlayerInteractEvent fired
  │
  ├─ Not holding wand? → return (event passes through)
  ├─ No permission? → return
  ├─ No clicked block? → return
  │
  ├─ LEFT_CLICK_BLOCK → setCorner1, cancel event
  ├─ RIGHT_CLICK_BLOCK → setCorner2, cancel event
  │
  ├─ Both corners set? → show volume preview
  └─ Visualizer not active? → auto-enable
```

---

## 8. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Default event priority | No need to override other plugins' handling; wand clicks are cancelled anyway. |
| `setCancelled(true)` on wand clicks | Prevents block breaking/placing/interaction while using the wand. |
| Silent permission failure | Avoids chat spam if a non-permitted player accidentally holds the wand. |
| Auto-enable visualizer | Improves UX — players immediately see their selection without extra commands. |
| `peekRegion` for preview | Avoids consuming corners, which should only happen on explicit `/bl add`. |
| No event priority specification | NORMAL priority is sufficient since we cancel early and only for wand holders. |
