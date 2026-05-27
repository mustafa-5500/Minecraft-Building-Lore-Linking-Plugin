# CuboidRegion — Software Detailed Design

> **API Documentation:** [CuboidRegion.md](./CuboidRegion.md)  
> **Source File:** [CuboidRegion.java](../../src/main/java/org/almond/buildinglore/model/CuboidRegion.java)

---

## 1. Overview

`CuboidRegion` is an immutable value object representing an axis-aligned bounding box (AABB) in a Minecraft world. It stores normalized min/max coordinates and provides spatial query methods (containment, overlap, adjacency), set operations (merge, intersect, subtract), and serialization.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.model;
```

```java
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;
```

| Import | Purpose |
|--------|---------|
| `HashSet` | Used to collect region fragments in `subtract()` |
| `Objects` | Provides `Objects.hash(...)` for `hashCode()` implementation |
| `Set` | Return type for `subtract()` and `Set.of()` factory |

---

## 3. Class Declaration & Javadoc

```java
/**
 * A cuboid region defined by two corners (min and max block coordinates).
 * Adapted from org.almond.lands.model.Region for Paper/Bukkit.
 */
public class CuboidRegion {
```

Immutable by design — all fields are `final` and there are no setter methods.

---

## 4. Instance Fields

```java
private final String worldName;
private final int minX, minY, minZ;
private final int maxX, maxY, maxZ;
```

| Field | Type | Description |
|-------|------|-------------|
| `worldName` | `String` | Name of the Minecraft world this region belongs to |
| `minX`, `minY`, `minZ` | `int` | Minimum corner coordinates (inclusive) |
| `maxX`, `maxY`, `maxZ` | `int` | Maximum corner coordinates (inclusive) |

All coordinates are block-level integers. The min/max normalization ensures `minX <= maxX`, etc., regardless of input order.

---

## 5. Constructor

```java
/** Constructor — corners are normalized to min/max automatically */
public CuboidRegion(String worldName, int x1, int y1, int z1, int x2, int y2, int z2) {
    this.worldName = worldName;
    this.minX = Math.min(x1, x2);
    this.minY = Math.min(y1, y2);
    this.minZ = Math.min(z1, z2);
    this.maxX = Math.max(x1, x2);
    this.maxY = Math.max(y1, y2);
    this.maxZ = Math.max(z1, z2);
}
```

- Accepts two arbitrary corners (no ordering requirement).
- `Math.min`/`Math.max` ensures the invariant: `minX <= maxX`, `minY <= maxY`, `minZ <= maxZ`.
- This allows callers to pass corners in any order without pre-sorting.

---

## 6. `contains(int, int, int)`

```java
/** Checks if the given block position is within this region */
public boolean contains(int x, int y, int z) {
    return x >= minX && x <= maxX &&
           y >= minY && y <= maxY &&
           z >= minZ && z <= maxZ;
}
```

Standard AABB point containment test. All comparisons are inclusive (the boundary blocks are part of the region). O(1) time.

---

## 7. `overlaps(CuboidRegion)`

```java
/** Checks if this region overlaps with another region (same world only) */
public boolean overlaps(CuboidRegion other) {
    if (!this.worldName.equals(other.worldName)) return false;
    return this.minX <= other.maxX && this.maxX >= other.minX &&
           this.minY <= other.maxY && this.maxY >= other.minY &&
           this.minZ <= other.maxZ && this.maxZ >= other.minZ;
}
```

Two AABBs overlap if and only if they overlap on **all three axes** simultaneously. The world check prevents cross-world false positives.

---

## 8. `containsRegion(CuboidRegion)`

```java
/** Checks if this region fully contains another region */
public boolean containsRegion(CuboidRegion other) {
    if (!this.worldName.equals(other.worldName)) return false;
    return this.minX <= other.minX && this.maxX >= other.maxX &&
           this.minY <= other.minY && this.maxY >= other.maxY &&
           this.minZ <= other.minZ && this.maxZ >= other.maxZ;
}
```

Full containment: every block of `other` is also within `this`. This is a strict subset check on all three axis ranges.

---

## 9. `isAdjacentTo(CuboidRegion)`

```java
/** Checks if this region is adjacent (touching face-to-face) to another region */
public boolean isAdjacentTo(CuboidRegion other) {
    if (!this.worldName.equals(other.worldName)) return false;

    boolean xAdj = (this.maxX + 1 == other.minX || this.minX - 1 == other.maxX) &&
                   (this.minY <= other.maxY && this.maxY >= other.minY) &&
                   (this.minZ <= other.maxZ && this.maxZ >= other.minZ);

    boolean yAdj = (this.maxY + 1 == other.minY || this.minY - 1 == other.maxY) &&
                   (this.minX <= other.maxX && this.maxX >= other.minX) &&
                   (this.minZ <= other.maxZ && this.maxZ >= other.minZ);

    boolean zAdj = (this.maxZ + 1 == other.minZ || this.minZ - 1 == other.maxZ) &&
                   (this.minX <= other.maxX && this.maxX >= other.minX) &&
                   (this.minY <= other.maxY && this.maxY >= other.minY);

    return xAdj || yAdj || zAdj;
}
```

Two regions are **adjacent** if:
1. They are exactly 1 block apart along one axis (faces touch), AND
2. They overlap on the other two axes (the touching faces share area).

This is checked independently for X, Y, and Z adjacency. Only one direction needs to be true.

---

## 10. `isSamePlaneAs(CuboidRegion)`

```java
/** Checks if two regions share the same plane along 2 axes (mergeable) */
public boolean isSamePlaneAs(CuboidRegion other) {
    boolean xSame = this.minY == other.minY && this.maxY == other.maxY &&
                    this.minZ == other.minZ && this.maxZ == other.maxZ;

    boolean ySame = this.minX == other.minX && this.maxX == other.maxX &&
                    this.minZ == other.minZ && this.maxZ == other.maxZ;

    boolean zSame = this.minX == other.minX && this.maxX == other.maxX &&
                    this.minY == other.minY && this.maxY == other.maxY;

    return xSame || ySame || zSame;
}
```

Two regions are in the "same plane" if they differ only along **one** axis — meaning they share identical extents on the other two axes. This is a prerequisite for merging: merging two regions that differ on multiple axes would produce a non-rectangular result.

- `xSame` — same Y and Z ranges, differ only in X.
- `ySame` — same X and Z ranges, differ only in Y.
- `zSame` — same X and Y ranges, differ only in Z.

---

## 11. `merge(CuboidRegion)`

```java
/** Merge this region with another, producing the bounding box union */
public CuboidRegion merge(CuboidRegion other) {
    return new CuboidRegion(
        this.worldName,
        Math.min(this.minX, other.minX), Math.min(this.minY, other.minY), Math.min(this.minZ, other.minZ),
        Math.max(this.maxX, other.maxX), Math.max(this.maxY, other.maxY), Math.max(this.maxZ, other.maxZ)
    );
}
```

Produces the smallest AABB that contains both regions. This is only geometrically correct (no extra blocks included) when the regions are adjacent and same-plane.

---

## 12. `intersection(CuboidRegion)`

```java
/** Calculates the intersection with another region, or null if none */
public CuboidRegion intersection(CuboidRegion other) {
    if (!this.overlaps(other)) return null;
    return new CuboidRegion(
        this.worldName,
        Math.max(this.minX, other.minX), Math.max(this.minY, other.minY), Math.max(this.minZ, other.minZ),
        Math.min(this.maxX, other.maxX), Math.min(this.maxY, other.maxY), Math.min(this.maxZ, other.maxZ)
    );
}
```

Returns the overlapping sub-region, or `null` if the regions don't overlap. The intersection's min is the max of both mins, and its max is the min of both maxes.

---

## 13. `subtract(CuboidRegion)`

```java
/** Subtracts another region from this one and returns the remaining pieces */
public Set<CuboidRegion> subtract(CuboidRegion other) {
    if (!this.overlaps(other)) {
        return Set.of(this);
    }
    CuboidRegion inter = this.intersection(other);
    Set<CuboidRegion> remaining = new HashSet<>();
```

If there's no overlap, the original region is returned unchanged. Otherwise, computes the intersection to determine what to carve out.

```java
    // Left (negative X)
    if (this.minX < inter.minX) {
        remaining.add(new CuboidRegion(worldName, this.minX, this.minY, this.minZ, inter.minX - 1, this.maxY, this.maxZ));
    }
    // Right (positive X)
    if (this.maxX > inter.maxX) {
        remaining.add(new CuboidRegion(worldName, inter.maxX + 1, this.minY, this.minZ, this.maxX, this.maxY, this.maxZ));
    }
```

Slices off the left and right portions (full Y and Z extent of `this`).

```java
    // Bottom (negative Y) — constrained to intersection X range
    if (this.minY < inter.minY) {
        remaining.add(new CuboidRegion(worldName, inter.minX, this.minY, this.minZ, inter.maxX, inter.minY - 1, this.maxZ));
    }
    // Top (positive Y)
    if (this.maxY > inter.maxY) {
        remaining.add(new CuboidRegion(worldName, inter.minX, inter.maxY + 1, this.minZ, inter.maxX, this.maxY, this.maxZ));
    }
```

Bottom and top slabs — constrained to the intersection's X range to avoid overlapping with the left/right pieces.

```java
    // Front (negative Z) — constrained to intersection X and Y range
    if (this.minZ < inter.minZ) {
        remaining.add(new CuboidRegion(worldName, inter.minX, inter.minY, this.minZ, inter.maxX, inter.maxY, inter.minZ - 1));
    }
    // Back (positive Z)
    if (this.maxZ > inter.maxZ) {
        remaining.add(new CuboidRegion(worldName, inter.minX, inter.minY, inter.maxZ + 1, inter.maxX, inter.maxY, this.maxZ));
    }
    return remaining;
}
```

Front and back slabs — constrained to both the intersection's X and Y ranges. This 6-piece decomposition ensures:
- No overlap between result pieces.
- All pieces together with the intersection exactly reconstruct `this`.
- The intersection itself is excluded (subtracted).

---

## 14. `getVolume()`

```java
/** Block count of this cuboid */
public long getVolume() {
    return (long)(maxX - minX + 1) * (maxY - minY + 1) * (maxZ - minZ + 1);
}
```

Since coordinates are inclusive, the length along each axis is `max - min + 1`. Cast to `long` prevents integer overflow for large regions (e.g., 1000×256×1000 = 256,000,000).

---

## 15. `toString()`

```java
@Override
public String toString() {
    return "(" + minX + "," + minY + "," + minZ + ")-(" + maxX + "," + maxY + "," + maxZ + ")";
}
```

Compact human-readable format: `(x1,y1,z1)-(x2,y2,z2)`. Used for:
- Player-facing messages.
- YAML serialization in `SelectionStorageManager`.

---

## 16. `fromString(String, String)` — Static Factory

```java
public static CuboidRegion fromString(String worldName, String s) {
    String cleaned = s.replace("(", "").replace(")", "");
    String[] halves = cleaned.split("-", 2);
    String[] min = halves[0].split(",");
    String[] max = halves[1].split(",");
    return new CuboidRegion(
        worldName,
        Integer.parseInt(min[0].trim()), Integer.parseInt(min[1].trim()), Integer.parseInt(min[2].trim()),
        Integer.parseInt(max[0].trim()), Integer.parseInt(max[1].trim()), Integer.parseInt(max[2].trim())
    );
}
```

Parses the format produced by `toString()`:
1. Strips parentheses.
2. Splits on `-` with limit 2 (to handle negative coordinates).
3. Splits each half on `,` to get 3 coordinate strings.
4. Parses integers with `trim()` for robustness.

**Note:** The split limit of 2 is critical — without it, negative coordinates (e.g., `-100`) would produce extra empty splits.

---

## 17. `equals(Object)` and `hashCode()`

```java
@Override
public boolean equals(Object obj) {
    if (this == obj) return true;
    if (obj == null || getClass() != obj.getClass()) return false;
    CuboidRegion other = (CuboidRegion) obj;
    return minX == other.minX && minY == other.minY && minZ == other.minZ &&
           maxX == other.maxX && maxY == other.maxY && maxZ == other.maxZ &&
           worldName.equals(other.worldName);
}

@Override
public int hashCode() {
    return Objects.hash(worldName, minX, minY, minZ, maxX, maxY, maxZ);
}
```

Value equality based on all seven fields. This is essential for using `CuboidRegion` in `HashSet` (e.g., in `subtract()`).

---

## 18. Getters

```java
public String getWorldName() { return worldName; }
public int getMinX() { return minX; }
public int getMinY() { return minY; }
public int getMinZ() { return minZ; }
public int getMaxX() { return maxX; }
public int getMaxY() { return maxY; }
public int getMaxZ() { return maxZ; }
```

Standard accessor methods. Single-line style for brevity.

---

## 19. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Immutable (all fields `final`, no setters) | Thread safety; prevents accidental mutation; safe to share |
| Auto-normalize min/max in constructor | Callers never need to pre-sort corners |
| `long` return for `getVolume()` | Prevents overflow for large selections |
| 6-piece subtract decomposition | Guarantees non-overlapping result pieces |
| `String` world name (not `World` reference) | Avoids holding Bukkit object references; serialization-friendly |
| `equals`/`hashCode` on all fields | Required for `HashSet` usage in `subtract` and `Selection.addRegion` |
| `fromString` split limit of 2 | Correctly handles negative coordinate values |
