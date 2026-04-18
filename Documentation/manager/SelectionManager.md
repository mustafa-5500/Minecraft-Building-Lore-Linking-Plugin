# SelectionManager.java
[[SelectionManager.java]]

Manages per-player selection state for building cuboid regions with the wand. Stores two corner locations per player in memory (not persisted) and provides methods to build a `CuboidRegion` from them. Adapted from `org.almond.lands.manager.SelectionManager`.

**Fields:**
- `corner1` — Map of player UUID → first corner `Location`
- `corner2` — Map of player UUID → second corner `Location`

**Functions:**
[[setCorner1]]
[[setCorner2]]
[[getCorners]]
[[hasCompleteSelection]]
[[buildRegion]]
[[peekRegion]]
[[clearSelection]]

---

## setCorner1

### Signature
```java
public void setCorner1(UUID playerId, Location location)
```

### Description
Stores the first corner position for the given player's pending region selection.

### Parameters
| Name       | Type       | Description                              |
| ---------- | ---------- | ---------------------------------------- |
| `playerId` | `UUID`     | The player's unique ID                   |
| `location` | `Location` | The Bukkit location to store as corner 1 |

### Returns
`void`

---

## setCorner2

### Signature
```java
public void setCorner2(UUID playerId, Location location)
```

### Description
Stores the second corner position for the given player's pending region selection.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |
| `location` | `Location` | The Bukkit location to store as corner 2 |

### Returns
`void`

---

## getCorner1 / getCorner2

### Signatures
```java
public Location getCorner1(UUID playerId)
public Location getCorner2(UUID playerId)
```

### Description
Retrieves the stored corner location for a player. Returns `null` if the corner has not been set.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

### Returns
`Location` or `null`.

---

## hasCompleteSelection

### Signature
```java
public boolean hasCompleteSelection(UUID playerId)
```

### Description
Checks whether both corners are set for the player and that they are in the same world.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

### Returns
`boolean` — `true` if both corners are set and in the same world.

---

## buildRegion

### Signature
```java
public CuboidRegion buildRegion(UUID playerId)
```

### Description
Creates a `CuboidRegion` from the player's two stored corners, then clears the corner state. Returns `null` if the selection is incomplete.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

### Returns
`CuboidRegion` or `null` — the constructed region, or `null` if corners are not ready.

---

## peekRegion

### Signature
```java
public CuboidRegion peekRegion(UUID playerId)
```

### Description
Returns what the region would be from the current corners without consuming/clearing them. Useful for previewing the selection volume.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

### Returns
`CuboidRegion` or `null`.

---

## clearSelection

### Signature
```java
public void clearSelection(UUID playerId)
```

### Description
Removes both stored corners for the given player.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

### Returns
`void`
