# CuboidRegion.java
[[CuboidRegion.java]]

An immutable cuboid region defined by two corners (min and max block coordinates) within a named world. Corners are automatically normalized to min/max on construction. Provides spatial operations including containment checks, overlap detection, adjacency testing, merging, intersection, and subtraction. Adapted from `org.almond.lands.model.Region`.

**Fields:**
- `worldName` — The name of the world this region belongs to
- `minX`, `minY`, `minZ` — Minimum corner coordinates
- `maxX`, `maxY`, `maxZ` — Maximum corner coordinates

**Functions:**
[[constructor]]
[[contains]]
[[overlaps]]
[[isAdjacentTo]]
[[isSamePlaneAs]]
[[merge]]
[[intersection]]
[[subtract]]
[[getVolume]]
[[toString]]
[[fromString]]
[[equals_hashCode]]
[[getters]]

---

## CuboidRegion (Constructor)

### Signature
```java
public CuboidRegion(String worldName, int x1, int y1, int z1, int x2, int y2, int z2)
```

### Description
Creates a cuboid region from two arbitrary corner positions. The coordinates are automatically normalized so that `min` values are always less than or equal to `max` values.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `worldName` | `String` | The name of the world this region belongs to |
| `x1` | `int` | X coordinate of the first corner |
| `y1` | `int` | Y coordinate of the first corner |
| `z1` | `int` | Z coordinate of the first corner |
| `x2` | `int` | X coordinate of the second corner |
| `y2` | `int` | Y coordinate of the second corner |
| `z2` | `int` | Z coordinate of the second corner |

### Returns
A new `CuboidRegion` instance.

---

## contains

### Signature
```java
public boolean contains(int x, int y, int z)
```

### Description
Checks if the given block coordinate falls within this cuboid region (inclusive on all boundaries).

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `x` | `int` | X coordinate to test |
| `y` | `int` | Y coordinate to test |
| `z` | `int` | Z coordinate to test |

### Returns
`boolean` — `true` if the point is inside or on the boundary of the cuboid.

---

## overlaps

### Signature
```java
public boolean overlaps(CuboidRegion other)
```

### Description
Checks if this region overlaps (shares any block coordinates) with another region. Regions in different worlds never overlap.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The other region to test against |

### Returns
`boolean` — `true` if the two regions share at least one block coordinate.

---

## isAdjacentTo

### Signature
```java
public boolean isAdjacentTo(CuboidRegion other)
```

### Description
Checks if this region is adjacent (touching face-to-face, with no gap and no overlap) to another region. Tests all three axes. Regions must be in the same world.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The other region to test against |

### Returns
`boolean` — `true` if the regions share a face along any axis.

---

## isSamePlaneAs

### Signature
```java
public boolean isSamePlaneAs(CuboidRegion other)
```

### Description
Checks if two regions share the same extents along two of the three axes, meaning they could be merged into a single cuboid along the remaining axis.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The other region to compare |

### Returns
`boolean` — `true` if the regions are coplanar along two axes.

---

## merge

### Signature
```java
public CuboidRegion merge(CuboidRegion other)
```

### Description
Merges this region with another by producing the bounding box union (the smallest cuboid that contains both regions).

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The region to merge with |

### Returns
`CuboidRegion` — a new region representing the bounding box of both inputs.

---

## intersection

### Signature
```java
public CuboidRegion intersection(CuboidRegion other)
```

### Description
Calculates the overlapping sub-region shared by this region and another. Returns `null` if the regions do not overlap.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The other region to intersect with |

### Returns
`CuboidRegion` or `null` — the intersection cuboid, or `null` if no overlap exists.

---

## subtract

### Signature
```java
public Set<CuboidRegion> subtract(CuboidRegion other)
```

### Description
Subtracts another region from this one, returning the set of remaining cuboid pieces. If there is no overlap, returns a set containing only this region. Splits along all three axes (up to 6 remaining pieces).

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The region to subtract |

### Returns
`Set<CuboidRegion>` — the remaining cuboid fragments after subtraction.

---

## getVolume

### Signature
```java
public long getVolume()
```

### Description
Returns the total number of blocks contained in this cuboid region.

### Parameters
None.

### Returns
`long` — the block count `(maxX - minX + 1) * (maxY - minY + 1) * (maxZ - minZ + 1)`.

---

## toString

### Signature
```java
@Override
public String toString()
```

### Description
Returns a compact string representation of the region in the format `(minX,minY,minZ)-(maxX,maxY,maxZ)`. Used for serialization and display.

### Parameters
None.

### Returns
`String` — e.g. `(10,64,20)-(25,80,35)`.

---

## fromString

### Signature
```java
public static CuboidRegion fromString(String worldName, String s)
```

### Description
Parses a compact string (produced by `toString()`) back into a `CuboidRegion`. Expected format: `(x1,y1,z1)-(x2,y2,z2)`.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `worldName` | `String` | The world to associate the region with |
| `s` | `String` | The string to parse |

### Returns
`CuboidRegion` — the parsed region.

---

## equals / hashCode

### Signatures
```java
@Override
public boolean equals(Object obj)

@Override
public int hashCode()
```

### Description
Two `CuboidRegion` instances are equal if they have the same world name and identical min/max coordinates. `hashCode` is consistent with `equals`, computed from all seven fields.

### Parameters (equals)
| Name | Type | Description |
|------|------|-------------|
| `obj` | `Object` | The object to compare |

### Returns
- `equals`: `boolean` — `true` if both regions define the same cuboid in the same world.
- `hashCode`: `int` — hash derived from `worldName`, `minX`, `minY`, `minZ`, `maxX`, `maxY`, `maxZ`.

---

## Getters

### Signatures
```java
public String getWorldName()
public int getMinX()
public int getMinY()
public int getMinZ()
public int getMaxX()
public int getMaxY()
public int getMaxZ()
```

### Description
Accessors for the region's immutable fields: world name and the six normalized corner coordinates.
