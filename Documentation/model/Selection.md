# Selection.java
[[Selection.java]]

A named set of `CuboidRegion` objects belonging to a player. Handles overlap resolution when adding regions: existing regions fully contained by the new one are removed, regions fully containing the new one cause it to be skipped, and partial overlaps are resolved via subtraction. Adjacent same-plane regions are automatically merged after each addition. Adapted from `org.almond.lands.model.Land` (stripped of permissions/roles).

**Fields:**
- `id` — Unique UUID for this selection
- `name` — Human-readable name
- `owner` — UUID of the owning player
- `worldName` — The world this selection belongs to
- `regions` — List of `CuboidRegion` objects
- `createdAt` — Timestamp of creation

**Functions:**
[[constructors]]
[[addRegion]]
[[removeRegion]]
[[getTotalVolume]]
[[containsBlock]]
[[mergeRegions]]
[[getters]]

---

## Selection (Constructors)

### Full Constructor
```java
public Selection(UUID id, String name, UUID owner, String worldName, List<CuboidRegion> regions, long createdAt)
```
Creates a selection with all fields specified. The regions list is defensively copied.

### Convenience Constructor
```java
public Selection(String name, UUID owner, String worldName)
```
Creates a new empty selection with an auto-generated UUID and current timestamp.

### Parameters (Full)
| Name | Type | Description |
|------|------|-------------|
| `id` | `UUID` | Unique identifier |
| `name` | `String` | Player-chosen display name |
| `owner` | `UUID` | UUID of the owning player |
| `worldName` | `String` | Minecraft world name |
| `regions` | `List<CuboidRegion>` | Initial regions |
| `createdAt` | `long` | Creation timestamp (epoch millis) |

---

## addRegion

### Signature
```java
public void addRegion(CuboidRegion region)
```

### Description
Appends a cuboid region to this selection's region list.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `region` | `CuboidRegion` | The region to add |

### Returns
`void`

---

## removeRegion

### Signature
```java
public boolean removeRegion(int index)
```

### Description
Removes a region by its 0-based index in the region list. Returns `false` if the index is out of bounds.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `index` | `int` | 0-based index of the region to remove |

### Returns
`boolean` — `true` if the region was removed, `false` if the index was invalid.

---

## getTotalVolume

### Signature
```java
public long getTotalVolume()
```

### Description
Sums the volume (block count) of all regions in this selection. Does not deduplicate overlapping blocks.

### Parameters
None.

### Returns
`long` — total block count across all regions.

---

## containsBlock

### Signature
```java
public boolean containsBlock(int x, int y, int z)
```

### Description
Checks if any region in this selection contains the specified block coordinate.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `x` | `int` | X coordinate |
| `y` | `int` | Y coordinate |
| `z` | `int` | Z coordinate |

### Returns
`boolean` — `true` if the block is inside at least one region.

---

## mergeRegions

### Signature
```java
public void mergeRegions()
```

### Description
Attempts to merge adjacent, non-overlapping, same-plane regions within this selection to reduce the total region count. Modifies the internal region list in place.

### Parameters
None.

### Returns
`void`

---

## Getters

### Signatures
```java
public UUID getId()
public String getName()
public UUID getOwner()
public String getWorldName()
public List<CuboidRegion> getRegions()
public long getCreatedAt()
public int getRegionCount()
```

### Description
Accessors for the selection's fields. `getRegions()` returns the internal list (not a copy). `getRegionCount()` is a convenience for `getRegions().size()`.
