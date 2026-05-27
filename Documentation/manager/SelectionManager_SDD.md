# SelectionManager — Software Detailed Design

> **API Documentation:** [SelectionManager.md](./SelectionManager.md)  
> **Source File:** [SelectionManager.java](../../src/main/java/org/almond/buildinglore/manager/SelectionManager.java)

---

## 1. Overview

`SelectionManager` maintains per-player **ephemeral** wand corner state in memory. It provides methods to set, get, and clear the two corners of a cuboid selection, check completeness, and construct `CuboidRegion` objects. This state is intentionally not persisted — it resets on server restart or when corners are consumed via `buildRegion`.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.manager;
```

```java
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.almond.buildinglore.model.CuboidRegion;
import org.bukkit.Location;
```

| Import | Purpose |
|--------|---------|
| `HashMap` | Backing data structure for corner storage |
| `Map` | Interface type for the field declarations |
| `UUID` | Player unique identifier used as map key |
| `CuboidRegion` | The model class constructed from two corner locations |
| `Location` | Bukkit class representing a 3D position with world reference |

---

## 3. Class Declaration & Javadoc

```java
/**
 * Per-player ephemeral state for building cuboid regions with a wand.
 * Adapted from org.almond.lands.manager.SelectionManager.
 */
public class SelectionManager {
```

The Javadoc notes this class was adapted from a prior project (`org.almond.lands`), indicating the design pattern is proven.

---

## 4. Instance Fields

```java
private final Map<UUID, Location> corner1 = new HashMap<>();
private final Map<UUID, Location> corner2 = new HashMap<>();
```

| Field | Key | Value | Notes |
|-------|-----|-------|-------|
| `corner1` | Player UUID | The Location of their first corner | Eagerly initialized, never replaced |
| `corner2` | Player UUID | The Location of their second corner | Same structure |

Two separate maps (rather than a single map to a pair/tuple) keeps the API simple — each corner is independently settable.

---

## 5. `setCorner1(UUID, Location)`

```java
public void setCorner1(UUID playerId, Location location) {
    corner1.put(playerId, location);
}
```

- Inserts or replaces the corner 1 entry for the given player.
- `HashMap.put` is O(1) amortized.
- No validation — any non-null Location is accepted. The completeness check happens later.

---

## 6. `setCorner2(UUID, Location)`

```java
public void setCorner2(UUID playerId, Location location) {
    corner2.put(playerId, location);
}
```

Identical pattern to `setCorner1` but for the second corner.

---

## 7. `getCorner1(UUID)` / `getCorner2(UUID)`

```java
public Location getCorner1(UUID playerId) {
    return corner1.get(playerId);
}

public Location getCorner2(UUID playerId) {
    return corner2.get(playerId);
}
```

- Returns the stored `Location` or `null` if the player hasn't set that corner.
- Used by `SelectionVisualizer` to render single-point markers when only one corner is set.

---

## 8. `hasCompleteSelection(UUID)`

```java
/** Both corners are set and in the same world */
public boolean hasCompleteSelection(UUID playerId) {
    Location c1 = corner1.get(playerId);
    Location c2 = corner2.get(playerId);
    if (c1 == null || c2 == null) return false;
    if (c1.getWorld() == null || c2.getWorld() == null) return false;
    return c1.getWorld().equals(c2.getWorld());
}
```

**Validation logic:**
1. Both corners must exist (not null).
2. Both locations must have a non-null world reference (world could be unloaded).
3. Both locations must be in the **same** world — cross-world selections are not supported.

Returns `true` only when all three conditions are satisfied.

---

## 9. `buildRegion(UUID)`

```java
/** Build a CuboidRegion from the two corners, then clear them */
public CuboidRegion buildRegion(UUID playerId) {
    if (!hasCompleteSelection(playerId)) return null;
    Location c1 = corner1.get(playerId);
    Location c2 = corner2.get(playerId);
    CuboidRegion region = new CuboidRegion(
        c1.getWorld().getName(),
        c1.getBlockX(), c1.getBlockY(), c1.getBlockZ(),
        c2.getBlockX(), c2.getBlockY(), c2.getBlockZ()
    );
    clearSelection(playerId);
    return region;
}
```

**Behavior:**
1. Pre-condition check via `hasCompleteSelection` — returns `null` if not ready.
2. Reads both locations from the maps.
3. Constructs a `CuboidRegion` using:
   - `c1.getWorld().getName()` — the world name string (not the object reference).
   - `getBlockX/Y/Z()` — integer block coordinates from both locations.
   - The `CuboidRegion` constructor normalizes min/max internally.
4. **Clears** both corners via `clearSelection` — this is a "consume" operation. The selection is one-time-use.
5. Returns the constructed region.

This "consume and clear" pattern prevents accidental reuse of stale corners.

---

## 10. `peekRegion(UUID)`

```java
/** Peek at what the region would be without consuming the corners */
public CuboidRegion peekRegion(UUID playerId) {
    if (!hasCompleteSelection(playerId)) return null;
    Location c1 = corner1.get(playerId);
    Location c2 = corner2.get(playerId);
    return new CuboidRegion(
        c1.getWorld().getName(),
        c1.getBlockX(), c1.getBlockY(), c1.getBlockZ(),
        c2.getBlockX(), c2.getBlockY(), c2.getBlockZ()
    );
}
```

Identical to `buildRegion` except it does **not** call `clearSelection`. Used for:
- Volume previews in `WandListener`.
- Particle rendering in `SelectionVisualizer`.
- Preview display in `BuildingLoreCommand.showPreview`.

---

## 11. `clearSelection(UUID)`

```java
public void clearSelection(UUID playerId) {
    corner1.remove(playerId);
    corner2.remove(playerId);
}
```

Removes both corner entries for the player. After this, `hasCompleteSelection` returns `false` and `getCorner1`/`getCorner2` return `null`.

---

## 12. Memory Characteristics

| Property | Value |
|----------|-------|
| Persistence | None — purely in-memory |
| Thread safety | Not synchronized — assumes single-threaded access (Bukkit main thread) |
| Memory per player | Two `Location` objects (~64 bytes each) |
| Cleanup | Entries removed on `buildRegion` or `clearSelection`; no automatic eviction for offline players |

---

## 13. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Two separate `HashMap` fields | Simpler API than a single map to a `Pair<Location, Location>` |
| `buildRegion` clears corners | Prevents stale corner reuse; forces explicit re-selection |
| `peekRegion` as read-only alternative | Needed for preview/visualization without side effects |
| World equality check in `hasCompleteSelection` | Cross-world cuboids are geometrically meaningless |
| No thread synchronization | All callers are event handlers and commands running on the Bukkit main thread |
| No timeout/expiry for old corners | Simplicity; players can override by clicking new positions |
