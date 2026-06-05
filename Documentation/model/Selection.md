# Selection

> **Software Detailed Documentation:** [Selection_SDD.md](./Selection_SDD.md)  
> **Source File:** [Selection.java](../../src/main/java/org/almond/buildinglore/model/Selection.java)

A named set of [`CuboidRegion`](CuboidRegion.md) objects belonging to a player. Handles overlap resolution when adding regions: existing regions fully contained by the new one are removed, regions fully containing the new one cause it to be skipped, and partial overlaps are resolved via subtraction. Adjacent same-plane regions are automatically merged after each addition. Adapted from `org.almond.lands.model.Land` (stripped of permissions/roles).

**Fields:**
- `id` — Unique UUID for this selection
- `name` — Human-readable name
- `owner` — UUID of the owning player
- `worldName` — The world this selection belongs to
- `regions` — List of [`CuboidRegion`](CuboidRegion.md) objects
- `createdAt` — Timestamp of creation
- `loreDocuments` (`Map<String, LoreDocument>`) — TODO: describe field

**Functions:**
- [constructors](#selection-constructors)
- [addRegion](#addregion)
- [removeRegion](#removeregion)
- [getTotalVolume](#gettotalvolume)
- [containsBlock](#containsblock)
- [mergeRegions](#mergeregions)
- [getters](#getters)
- [Selection (Constructor)](#selection)
- [Selection (Constructor)](#selection)
- [addLoreDocument](#addloredocument)
- [getLoreDocument](#getloredocument)
- [removeLoreDocument](#removeloredocument)
- [getLoreDocuments](#getloredocuments)
- [getId](#getid)
- [getName](#getname)
- [getOwner](#getowner)
- [getWorldName](#getworldname)
- [getRegions](#getregions)
- [getCreatedAt](#getcreatedat)
- [getRegionCount](#getregioncount)

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
| `region` | [`CuboidRegion`](CuboidRegion.md) | The region to add |

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

## Selection (Constructor)

### Signature
```java
public Selection(UUID id, String name, UUID owner, String worldName, List<CuboidRegion> regions, long createdAt)
```

### Description
TODO: Describe what `Selection` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `id` | `UUID` | TODO: describe |
| `name` | `String` | TODO: describe |
| `owner` | `UUID` | TODO: describe |
| `worldName` | `String` | TODO: describe |
| `regions` | `List<CuboidRegion>` | TODO: describe |
| `createdAt` | `long` | TODO: describe |

### Returns
`Selection` instance.

---

## Selection (Constructor)

### Signature
```java
public Selection(String name, UUID owner, String worldName)
```

### Description
TODO: Describe what `Selection` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `name` | `String` | TODO: describe |
| `owner` | `UUID` | TODO: describe |
| `worldName` | `String` | TODO: describe |

### Returns
`Selection` instance.

---

## addLoreDocument

### Signature
```java
public void addLoreDocument(LoreDocument doc)
```

### Description
TODO: Describe what `addLoreDocument` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `doc` | [`LoreDocument`](LoreDocument.md) | TODO: describe |

### Returns
`void`

---

## getLoreDocument

### Signature
```java
public LoreDocument getLoreDocument(String name)
```

### Description
TODO: Describe what `getLoreDocument` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `name` | `String` | TODO: describe |

### Returns
[`LoreDocument`](LoreDocument.md) — TODO: describe return value.

---

## removeLoreDocument

### Signature
```java
public boolean removeLoreDocument(String name)
```

### Description
TODO: Describe what `removeLoreDocument` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `name` | `String` | TODO: describe |

### Returns
`boolean` — TODO: describe return value.

---

## getLoreDocuments

### Signature
```java
public Map<String, LoreDocument> getLoreDocuments()
```

### Description
TODO: Describe what `getLoreDocuments` does.

### Parameters
None.

### Returns
`Map<String, LoreDocument>` — TODO: describe return value.

---

## getId

### Signature
```java
public UUID getId()
```

### Description
TODO: Describe what `getId` does.

### Parameters
None.

### Returns
`UUID` — TODO: describe return value.

---

## getName

### Signature
```java
public String getName()
```

### Description
TODO: Describe what `getName` does.

### Parameters
None.

### Returns
`String` — TODO: describe return value.

---

## getOwner

### Signature
```java
public UUID getOwner()
```

### Description
TODO: Describe what `getOwner` does.

### Parameters
None.

### Returns
`UUID` — TODO: describe return value.

---

## getWorldName

### Signature
```java
public String getWorldName()
```

### Description
TODO: Describe what `getWorldName` does.

### Parameters
None.

### Returns
`String` — TODO: describe return value.

---

## getRegions

### Signature
```java
public List<CuboidRegion> getRegions()
```

### Description
TODO: Describe what `getRegions` does.

### Parameters
None.

### Returns
`List<CuboidRegion>` — TODO: describe return value.

---

## getCreatedAt

### Signature
```java
public long getCreatedAt()
```

### Description
TODO: Describe what `getCreatedAt` does.

### Parameters
None.

### Returns
`long` — TODO: describe return value.

---

## getRegionCount

### Signature
```java
public int getRegionCount()
```

### Description
TODO: Describe what `getRegionCount` does.

### Parameters
None.

### Returns
`int` — TODO: describe return value.

---

## See Also:
- [SelectionManager](../manager/SelectionManager.md)
- [WandListener](../listener/WandListener.md)
- [CuboidRegion](../model/CuboidRegion.md)