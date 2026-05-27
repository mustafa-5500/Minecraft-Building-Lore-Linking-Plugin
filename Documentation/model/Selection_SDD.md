# Selection — Software Detailed Design

> **API Documentation:** [Selection.md](./Selection.md)  
> **Source File:** [Selection.java](../../src/main/java/org/almond/buildinglore/model/Selection.java)

---

## 1. Overview

`Selection` represents a named collection of `CuboidRegion` objects owned by a player, within a single Minecraft world. It provides intelligent region addition (with overlap resolution and merging), region removal, volume computation, block containment queries, and lore document attachment. This is the primary domain model persisted by `SelectionStorageManager`.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.model;
```

```java
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
```

| Import | Purpose |
|--------|---------|
| `ArrayList` | Mutable list for regions |
| `HashMap` | Lore document storage by name |
| `HashSet` | Working set for `addRegion` overlap resolution |
| `List`, `Map`, `Set` | Interface types |
| `UUID` | Selection and owner identifiers |

---

## 3. Class Declaration & Javadoc

```java
/**
 * A named set of CuboidRegions belonging to a player.
 * Adapted from org.almond.lands.model.Land (stripped of permissions/roles).
 */
public class Selection {
```

---

## 4. Instance Fields

```java
private final UUID id;
private final String name;
private final UUID owner;
private final String worldName;
private final List<CuboidRegion> regions;
private final Map<String, LoreDocument> loreDocuments;
private final long createdAt;
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Unique identifier for this selection |
| `name` | `String` | User-chosen name (also used as filename) |
| `owner` | `UUID` | Player UUID who owns this selection |
| `worldName` | `String` | Minecraft world this selection belongs to |
| `regions` | `List<CuboidRegion>` | Mutable list of non-overlapping regions |
| `loreDocuments` | `Map<String, LoreDocument>` | Named lore documents attached to this selection |
| `createdAt` | `long` | Unix timestamp (milliseconds) when created |

All identity fields (`id`, `name`, `owner`, `worldName`, `createdAt`) are `final`. The `regions` list reference is final but the list itself is mutable.

---

## 5. Full Constructor

```java
public Selection(UUID id, String name, UUID owner, String worldName, List<CuboidRegion> regions, long createdAt) {
    this.id = id;
    this.name = name;
    this.owner = owner;
    this.worldName = worldName;
    this.regions = new ArrayList<>(regions);
    this.loreDocuments = new HashMap<>();
    this.createdAt = createdAt;
}
```

- `new ArrayList<>(regions)` — defensive copy. Modifications to the passed-in list won't affect this selection.
- `loreDocuments` starts empty; documents are added separately via `addLoreDocument`.

---

## 6. Convenience Constructor

```java
/** Convenience constructor — generates a new UUID and timestamp */
public Selection(String name, UUID owner, String worldName) {
    this(UUID.randomUUID(), name, owner, worldName, new ArrayList<>(), System.currentTimeMillis());
}
```

Used when creating a brand-new selection from a command. Generates a random UUID and captures the current time.

---

## 7. `addRegion(CuboidRegion)` — Overlap Resolution

```java
public void addRegion(CuboidRegion region) {
```

This is the most complex method in the class. It implements a non-trivial overlap resolution algorithm adapted from `org.almond.lands.manager.LandManager.claimRegion`.

### 7.1 Full Containment Check

```java
    for (CuboidRegion existing : regions) {
        if (existing.containsRegion(region)) {
            return;
        }
    }
```

If any existing region already fully contains the new one, there's nothing to add — early return.

### 7.2 Remove Subsumed Regions

```java
    regions.removeIf(existing -> region.containsRegion(existing));
```

Any existing regions that are fully contained by the new region are redundant and removed. Uses `List.removeIf` with a predicate for conciseness.

### 7.3 Subtract Existing Overlaps

```java
    Set<CuboidRegion> toAdd = new HashSet<>();
    toAdd.add(region);
    for (CuboidRegion existing : regions) {
        Set<CuboidRegion> nextToAdd = new HashSet<>();
        for (CuboidRegion piece : toAdd) {
            if (existing.overlaps(piece)) {
                nextToAdd.addAll(piece.subtract(existing));
            } else {
                nextToAdd.add(piece);
            }
        }
        toAdd = nextToAdd;
    }
```

**Algorithm:**
1. Start with the new region as the only piece to add.
2. For each existing region, check every pending piece for overlap.
3. If they overlap, replace the piece with its subtraction fragments (the parts that don't overlap with the existing region).
4. If they don't overlap, keep the piece unchanged.
5. After processing all existing regions, `toAdd` contains only non-overlapping fragments.

This ensures no block is counted twice across all regions in the selection.

### 7.4 Add Fragments and Merge

```java
    regions.addAll(toAdd);
    mergeRegions();
}
```

Appends the non-overlapping fragments to the region list, then attempts to merge adjacent same-plane regions to reduce the total count.

---

## 8. `removeRegion(int)`

```java
public boolean removeRegion(int index) {
    if (index < 0 || index >= regions.size()) return false;
    regions.remove(index);
    return true;
}
```

Bounds-checked removal by 0-based index. Returns `false` if the index is invalid.

---

## 9. `getTotalVolume()`

```java
public long getTotalVolume() {
    long total = 0;
    for (CuboidRegion region : regions) {
        total += region.getVolume();
    }
    return total;
}
```

Sums the volume of all regions. Because `addRegion` ensures no overlaps, this is an accurate total block count.

---

## 10. `containsBlock(int, int, int)`

```java
public boolean containsBlock(int x, int y, int z) {
    for (CuboidRegion region : regions) {
        if (region.contains(x, y, z)) return true;
    }
    return false;
}
```

Linear scan — checks if any region contains the given block coordinates. Early-returns on first hit.

---

## 11. `mergeRegions()`

```java
public void mergeRegions() {
    boolean changed = true;
    while (changed) {
        changed = false;
        List<CuboidRegion> merged = new ArrayList<>();
        for (CuboidRegion region : this.regions) {
            boolean wasMerged = false;
            for (int i = 0; i < merged.size(); i++) {
                CuboidRegion existing = merged.get(i);
                if (existing.isAdjacentTo(region) && !existing.overlaps(region) && existing.isSamePlaneAs(region)) {
                    merged.set(i, existing.merge(region));
                    wasMerged = true;
                    changed = true;
                    break;
                }
            }
            if (!wasMerged) {
                merged.add(region);
            }
        }
        this.regions.clear();
        this.regions.addAll(merged);
    }
}
```

**Iterative merge algorithm:**
1. Outer loop runs until no merges occur in a pass.
2. For each region, try to find an existing merged region that is:
   - Adjacent (touching face-to-face).
   - Not overlapping (safety check).
   - Same-plane (differ on only one axis).
3. If found, replace the existing entry with the merged result.
4. If not mergeable with anything, add as-is to the merged list.
5. Replace `this.regions` with the merged result and repeat.

The iterative approach handles chains: A adjacent to B, B adjacent to C → merging A+B first, then (A+B)+C on the next pass.

---

## 12. Lore Document Methods

```java
public void addLoreDocument(LoreDocument doc) {
    loreDocuments.put(doc.getName(), doc);
}
```

Adds or replaces a document by name.

```java
public LoreDocument getLoreDocument(String name) {
    return loreDocuments.get(name);
}
```

Returns `null` if not found.

```java
public boolean removeLoreDocument(String name) {
    return loreDocuments.remove(name) != null;
}
```

Returns `true` if a document was actually removed.

```java
public Map<String, LoreDocument> getLoreDocuments() {
    return loreDocuments;
}
```

Returns the backing map directly (no defensive copy).

---

## 13. Getter Methods

```java
public UUID getId() { return id; }
public String getName() { return name; }
public UUID getOwner() { return owner; }
public String getWorldName() { return worldName; }
public List<CuboidRegion> getRegions() { return regions; }
public long getCreatedAt() { return createdAt; }
public int getRegionCount() { return regions.size(); }
```

Standard accessors. `getRegions()` returns the mutable list directly — callers can iterate but should not mutate externally.

---

## 14. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Overlap resolution in `addRegion` | Guarantees no duplicate blocks are counted; simplifies volume calculation |
| Iterative merge in `mergeRegions` | Handles transitive merge chains; terminates when stable |
| Mutable `regions` list | Regions are added/removed throughout the selection's lifetime |
| `UUID` for identity | Global uniqueness; safe for filenames and cross-reference |
| Single world per selection | Cross-world selections are geometrically meaningless |
| Lore documents stored by name | Fast lookup; enforces name uniqueness within a selection |
| `long` for `createdAt` | Unix milliseconds; timezone-independent; sortable |
