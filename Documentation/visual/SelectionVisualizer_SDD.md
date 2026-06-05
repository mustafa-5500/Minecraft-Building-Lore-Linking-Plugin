# SelectionVisualizer — Software Detailed Design

> **API Documentation:** [SelectionVisualizer.md](./SelectionVisualizer.md)  
> **Source File:** [SelectionVisualizer.java](../../src/main/java/org/almond/buildinglore/visual/SelectionVisualizer.java)

---

## 1. Overview

`SelectionVisualizer` draws particle outlines around players' current wand selections using Bukkit's particle API. It manages a repeating scheduled task that renders particles for all players who have visualization enabled, drawing the 12 edges of cuboid regions at configurable intervals and spacing.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.visual;
```

```java
import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.model.CuboidRegion;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
```

| Import | Purpose |
|--------|---------|
| [`SelectionManager`](../manager/SelectionManager.md) | Access to player corner data for rendering |
| [`CuboidRegion`](../model/CuboidRegion.md) | Region geometry for edge calculation |
| `Bukkit` | Server singleton access (scheduler, players, worlds) |
| `Color` | RGB color for dust particles |
| `Location` | 3D position for particle spawning |
| `Particle` | Particle type enum and `DustOptions` inner class |
| `World` | Required for particle spawning |
| `Player` | Target for player-specific particle rendering |
| `JavaPlugin` | Required for scheduler task registration |
| `BukkitTask` | Handle to the repeating task for cancellation |
| `HashSet`, `Set`, `UUID` | Player tracking data structures |

---

## 3. Class Declaration

```java
/**
 * Draws particle outlines around a player's current wand selection.
 * Particles are shown along the 12 edges of the cuboid at a configurable spacing.
 */
public class SelectionVisualizer {
```

---

## 4. Instance Fields

```java
private final JavaPlugin plugin;
private final SelectionManager selectionManager;
```

Injected dependencies for scheduler access and corner data.

```java
private final Set<UUID> enabledPlayers = new HashSet<>();
```

Tracks which players currently have visualization enabled. Players are added/removed via `toggle()`.

```java
private BukkitTask task;
```

The handle to the repeating scheduler task. `null` when no task is running (no players have visualization enabled).

---

## 5. Constants

```java
private static final double PARTICLE_SPACING = 0.5;
```

Distance in blocks between consecutive particles along an edge. `0.5` means 2 particles per block — provides a visually connected line without excessive particle count.

```java
private static final long REFRESH_INTERVAL = 10L;
```

Ticks between particle refreshes. `10L` ticks = 0.5 seconds. Particles are spawned as transient effects; this interval determines how "persistent" they appear.

---

## 6. Constructor

```java
public SelectionVisualizer(JavaPlugin plugin, SelectionManager selectionManager) {
    this.plugin = plugin;
    this.selectionManager = selectionManager;
}
```

No task is started at construction — it's lazy-started when the first player enables visualization.

---

## 7. `toggle(UUID)` — Enable/Disable

```java
public boolean toggle(UUID playerId) {
    if (enabledPlayers.contains(playerId)) {
        enabledPlayers.remove(playerId);
        stopIfNoViewers();
        return false;
    } else {
        enabledPlayers.add(playerId);
        startIfNeeded();
        return true;
    }
}
```

- If player is already enabled → remove and potentially stop the task. Returns `false` (now disabled).
- If player is not enabled → add and start the task if not running. Returns `true` (now enabled).

---

## 8. `isEnabled(UUID)` / `disable(UUID)`

```java
public boolean isEnabled(UUID playerId) {
    return enabledPlayers.contains(playerId);
}

public void disable(UUID playerId) {
    enabledPlayers.remove(playerId);
    stopIfNoViewers();
}
```

`isEnabled` — simple set membership check.
`disable` — unconditional removal (no toggle; always disables).

---

## 9. Task Lifecycle

### 9.1 `startIfNeeded()`

```java
private void startIfNeeded() {
    if (task != null) return;
    task = Bukkit.getScheduler().runTaskTimer(plugin, this::renderAll, 0L, REFRESH_INTERVAL);
}
```

- Guard: if task already running, do nothing.
- `runTaskTimer` — registers a repeating task on the Bukkit scheduler.
  - `plugin` — the owning plugin (for task tracking).
  - `this::renderAll` — method reference; called every `REFRESH_INTERVAL` ticks.
  - `0L` — initial delay (run immediately on first tick).
  - `REFRESH_INTERVAL` — period between executions (10 ticks).
- Stores the `BukkitTask` handle for later cancellation.

### 9.2 `stopIfNoViewers()`

```java
private void stopIfNoViewers() {
    if (!enabledPlayers.isEmpty()) return;
    if (task != null) {
        task.cancel();
        task = null;
    }
}
```

- Only stops if no players have visualization enabled.
- `task.cancel()` — removes the task from the scheduler.
- Sets `task = null` — allows `startIfNeeded` to create a new task later.

This lazy start/stop pattern ensures no scheduler resources are consumed when visualization isn't in use.

---

## 10. `renderAll()` — Main Render Loop

```java
private void renderAll() {
    for (UUID playerId : Set.copyOf(enabledPlayers)) {
        Player player = Bukkit.getPlayer(playerId);
        if (player == null || !player.isOnline()) {
            enabledPlayers.remove(playerId);
            continue;
        }
        renderForPlayer(player);
    }
    stopIfNoViewers();
}
```

- `Set.copyOf(enabledPlayers)` — creates a snapshot to avoid `ConcurrentModificationException` during removal.
- For each enabled player UUID:
  - Resolve to an online `Player` object.
  - If null or offline → remove from the set (cleanup stale entries).
  - Otherwise → render particles.
- After processing all players, check if the task should stop.

---

## 11. `renderForPlayer(Player)` — Per-Player Rendering

```java
private void renderForPlayer(Player player) {
    UUID playerId = player.getUniqueId();

    CuboidRegion preview = selectionManager.peekRegion(playerId);
    if (preview != null) {
        World world = Bukkit.getWorld(preview.getWorldName());
        if (world != null && world.equals(player.getWorld())) {
            drawCuboidEdges(player, world, preview, Color.LIME);
        }
    }
```

**Case 1: Both corners set** — draws the full cuboid outline in `LIME` (bright green).
- `peekRegion` returns non-null only when both corners are set in the same world.
- World check ensures particles aren't spawned in a different dimension.

```java
    } else {
        Location c1 = selectionManager.getCorner1(playerId);
        Location c2 = selectionManager.getCorner2(playerId);
        if (c1 != null && c1.getWorld() != null && c1.getWorld().equals(player.getWorld())) {
            spawnParticle(player, c1.getBlockX() + 0.5, c1.getBlockY() + 0.5, c1.getBlockZ() + 0.5, c1.getWorld(), Color.AQUA);
        }
        if (c2 != null && c2.getWorld() != null && c2.getWorld().equals(player.getWorld())) {
            spawnParticle(player, c2.getBlockX() + 0.5, c2.getBlockY() + 0.5, c2.getBlockZ() + 0.5, c2.getWorld(), Color.AQUA);
        }
    }
}
```

**Case 2: Only one corner (or incompatible worlds)** — renders individual corner markers in `AQUA` (cyan).
- `+ 0.5` offsets to the block center (particles look better centered).
- Each corner is independently checked for null and same-world.

---

## 12. `drawCuboidEdges(Player, World, CuboidRegion, Color)`

```java
private void drawCuboidEdges(Player player, World world, CuboidRegion region, Color color) {
    double x1 = region.getMinX();
    double y1 = region.getMinY();
    double z1 = region.getMinZ();
    double x2 = region.getMaxX() + 1.0;
    double y2 = region.getMaxY() + 1.0;
    double z2 = region.getMaxZ() + 1.0;
```

Converts block coordinates to edge coordinates. The `+ 1.0` is critical: block coordinates are inclusive, but the visual outline should wrap the **outside** of the selection. A block at (10, 64, 20) occupies space from 10.0 to 11.0, so the max edge of a selection ending at block 10 is at 11.0.

```java
    // 4 edges along X
    drawLine(player, world, x1, y1, z1, x2, y1, z1, color);
    drawLine(player, world, x1, y2, z1, x2, y2, z1, color);
    drawLine(player, world, x1, y1, z2, x2, y1, z2, color);
    drawLine(player, world, x1, y2, z2, x2, y2, z2, color);

    // 4 edges along Y
    drawLine(player, world, x1, y1, z1, x1, y2, z1, color);
    drawLine(player, world, x2, y1, z1, x2, y2, z1, color);
    drawLine(player, world, x1, y1, z2, x1, y2, z2, color);
    drawLine(player, world, x2, y1, z2, x2, y2, z2, color);

    // 4 edges along Z
    drawLine(player, world, x1, y1, z1, x1, y1, z2, color);
    drawLine(player, world, x2, y1, z1, x2, y1, z2, color);
    drawLine(player, world, x1, y2, z1, x1, y2, z2, color);
    drawLine(player, world, x2, y2, z1, x2, y2, z2, color);
}
```

A cuboid has 12 edges:
- 4 edges along the X axis (at the 4 combinations of min/max Y and Z).
- 4 edges along the Y axis (at the 4 combinations of min/max X and Z).
- 4 edges along the Z axis (at the 4 combinations of min/max X and Y).

Each edge is drawn as a particle line.

---

## 13. `drawLine(...)` — Parametric Line Drawing

```java
private void drawLine(Player player, World world, double x1, double y1, double z1,
                      double x2, double y2, double z2, Color color) {
    double dx = x2 - x1;
    double dy = y2 - y1;
    double dz = z2 - z1;
    double length = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (length == 0) return;
```

Calculates the direction vector and its Euclidean length. Returns early for zero-length lines (degenerate case).

```java
    int steps = Math.max(1, (int) (length / PARTICLE_SPACING));
    double stepX = dx / steps;
    double stepY = dy / steps;
    double stepZ = dz / steps;
```

Determines how many particles to place along the line based on the spacing constant. Divides the direction vector by the step count to get the per-step increment.

```java
    for (int i = 0; i <= steps; i++) {
        double px = x1 + stepX * i;
        double py = y1 + stepY * i;
        double pz = z1 + stepZ * i;
        spawnParticle(player, px, py, pz, world, color);
    }
}
```

Iterates from 0 to `steps` (inclusive — includes both endpoints). Computes each particle position by linear interpolation and spawns it.

---

## 14. `spawnParticle(...)` — Player-Specific Particle

```java
private void spawnParticle(Player player, double x, double y, double z, World world, Color color) {
    Particle.DustOptions dust = new Particle.DustOptions(color, 0.7f);
    player.spawnParticle(Particle.DUST, new Location(world, x, y, z), 1, 0, 0, 0, 0, dust);
}
```

- `Particle.DustOptions` — configures the `DUST` particle type with a color and size (0.7 = slightly smaller than default 1.0).
- `player.spawnParticle(...)` — sends the particle **only to this player**. Other players don't see it.
  - `Particle.DUST` — colored dust particle type.
  - `new Location(world, x, y, z)` — spawn position.
  - `1` — particle count (one per position).
  - `0, 0, 0` — offset (no random spread).
  - `0` — speed (stationary).
  - `dust` — the extra data (color and size).

---

## 15. `shutdown()` — Cleanup

```java
public void shutdown() {
    if (task != null) {
        task.cancel();
        task = null;
    }
    enabledPlayers.clear();
}
```

Called from `BuildingLorePlugin.onDisable()`. Cancels the scheduler task and clears all state. Prevents orphaned tasks that could throw `IllegalPluginAccessException` after plugin reload.

---

## 16. Particle Budget Analysis

For a typical selection of 10×10×10 blocks:
- Edge length per axis: 11 blocks (10 + 1 for visual bounds).
- Particles per edge: `11 / 0.5 = 22`.
- Total particles per frame: `12 edges × 22 = 264`.
- Refresh rate: every 0.5 seconds.

This is well within Minecraft's particle rendering capabilities and network limits.

---

## 17. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Player-specific particles (`player.spawnParticle`) | Only the selecting player needs to see their outline; avoids visual noise for others |
| Lazy task start/stop | No scheduler overhead when nobody is using visualization |
| `Set.copyOf` in render loop | Safe iteration while removing offline players |
| `+1.0` on max coordinates | Draws outline around the selection boundary, not through block centers |
| `Color.LIME` for full selection | High visibility against most Minecraft backgrounds |
| `Color.AQUA` for single corners | Distinct from the selection outline; indicates incomplete state |
| 0.5 block particle spacing | Balance between visual continuity and particle count |
| 10-tick refresh interval | Smooth appearance without excessive server load |
| `DUST` particle type | Allows arbitrary color; no sound; client-side rendering |
