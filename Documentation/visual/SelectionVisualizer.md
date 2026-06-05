# SelectionVisualizer

> **Software Detailed Documentation:** [SelectionVisualizer_SDD.md](./SelectionVisualizer_SDD.md)  
> **Source File:** [SelectionVisualizer.java](../../src/main/java/org/almond/buildinglore/visual/SelectionVisualizer.java)

Draws particle outlines around a player's current wand selection. Uses a repeating Bukkit scheduler task to render colored dust particles along the 12 edges of the selected cuboid at a configurable spacing. The task only runs when at least one player has visualization enabled, and automatically stops when all players disable it.

**Constants:**
- `PARTICLE_SPACING` — Distance in blocks between particles along each edge (0.5)
- `REFRESH_INTERVAL` — Ticks between each particle refresh cycle (10 ticks = 0.5 seconds)

**Fields:**
- `plugin` — Reference to the owning `JavaPlugin` instance
- `selectionManager` — Used to read current corner positions
- `enabledPlayers` — Set of player UUIDs with visualization active
- `task` — The repeating `BukkitTask` handle, or null if not running
- `PARTICLE_SPACING` (`double`) — TODO: describe field
- `REFRESH_INTERVAL` (`long`) — TODO: describe field

**Functions:**
- [constructor](#selectionvisualizer-constructor)
- [toggle](#toggle)
- [isEnabled](#isenabled)
- [disable](#disable)
- [shutdown](#shutdown)
- [startIfNeeded](#startifneeded)
- [stopIfNoViewers](#stopifnoviewers)
- [renderAll](#renderall)
- [renderForPlayer](#renderforplayer)
- [drawCuboidEdges](#drawcuboidedges)
- [drawLine](#drawline)
- [spawnParticle](#spawnparticle)

---

## SelectionVisualizer (Constructor)

### Signature
```java
public SelectionVisualizer(JavaPlugin plugin, SelectionManager selectionManager)
```

### Description
Initializes the visualizer with references to the plugin and selection manager. Does not start the particle task — it begins lazily when the first player enables visualization.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `plugin` | `JavaPlugin` | The owning plugin instance (used for scheduling) |
| `selectionManager` | [`SelectionManager`](../manager/SelectionManager.md) | The manager to read corner positions from |

---

## toggle

### Signature
```java
public boolean toggle(UUID playerId)
```

### Description
Toggles particle visualization on or off for the given player. Starts the repeating render task if this is the first enabled player, or stops it if the last player disables visualization.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

### Returns
`boolean` — `true` if visualization is now enabled, `false` if disabled.

---

## isEnabled

### Signature
```java
public boolean isEnabled(UUID playerId)
```

### Description
Checks whether particle visualization is currently active for the given player.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

### Returns
`boolean` — `true` if visualization is enabled for this player.

---

## disable

### Signature
```java
public void disable(UUID playerId)
```

### Description
Explicitly disables particle visualization for the given player. Stops the repeating task if no players remain with visualization enabled.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

### Returns
`void`

---

## shutdown

### Signature
```java
public void shutdown()
```

### Description
Cancels the repeating particle task and clears all enabled players. Called during plugin disable to clean up resources.

### Returns
`void`

## startIfNeeded

### Signature
```java
private void startIfNeeded()
```

### Description
TODO: Describe what `startIfNeeded` does.

### Parameters
None.

### Returns
`void`

---

## stopIfNoViewers

### Signature
```java
private void stopIfNoViewers()
```

### Description
TODO: Describe what `stopIfNoViewers` does.

### Parameters
None.

### Returns
`void`

---

## renderAll

### Signature
```java
private void renderAll()
```

### Description
TODO: Describe what `renderAll` does.

### Parameters
None.

### Returns
`void`

---

## renderForPlayer

### Signature
```java
private void renderForPlayer(Player player)
```

### Description
TODO: Describe what `renderForPlayer` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `Player` | TODO: describe |

### Returns
`void`

---

## drawCuboidEdges

### Signature
```java
private void drawCuboidEdges(Player player, World world, CuboidRegion region, Color color)
```

### Description
TODO: Describe what `drawCuboidEdges` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `Player` | TODO: describe |
| `world` | `World` | TODO: describe |
| `region` | [`CuboidRegion`](../model/CuboidRegion.md) | TODO: describe |
| `color` | `Color` | TODO: describe |

### Returns
`void`

---

## drawLine

### Signature
```java
private void drawLine(Player player, World world, double x1, double y1, double z1,
                          double x2, double y2, double z2, Color color)
```

### Description
TODO: Describe what `drawLine` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `Player` | TODO: describe |
| `world` | `World` | TODO: describe |
| `x1` | `double` | TODO: describe |
| `y1` | `double` | TODO: describe |
| `z1` | `double` | TODO: describe |
| `x2` | `double` | TODO: describe |
| `y2` | `double` | TODO: describe |
| `z2` | `double` | TODO: describe |
| `color` | `Color` | TODO: describe |

### Returns
`void`

---

## spawnParticle

### Signature
```java
private void spawnParticle(Player player, double x, double y, double z, World world, Color color)
```

### Description
TODO: Describe what `spawnParticle` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `Player` | TODO: describe |
| `x` | `double` | TODO: describe |
| `y` | `double` | TODO: describe |
| `z` | `double` | TODO: describe |
| `world` | `World` | TODO: describe |
| `color` | `Color` | TODO: describe |

### Returns
`void`

---

## See Also

- **Software Detailed Design:** [SelectionVisualizer_SDD.md](./SelectionVisualizer_SDD.md)
