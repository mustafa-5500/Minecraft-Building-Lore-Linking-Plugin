# SelectionVisualizer.java
[[SelectionVisualizer.java]]

Draws particle outlines around a player's current wand selection. Uses a repeating Bukkit scheduler task to render colored dust particles along the 12 edges of the selected cuboid at a configurable spacing. The task only runs when at least one player has visualization enabled, and automatically stops when all players disable it.

**Constants:**
- `PARTICLE_SPACING` — Distance in blocks between particles along each edge (0.5)
- `REFRESH_INTERVAL` — Ticks between each particle refresh cycle (10 ticks = 0.5 seconds)

**Fields:**
- `plugin` — Reference to the owning `JavaPlugin` instance
- `selectionManager` — Used to read current corner positions
- `enabledPlayers` — Set of player UUIDs with visualization active
- `task` — The repeating `BukkitTask` handle, or null if not running

**Functions:**
[[constructor]]
[[toggle]]
[[isEnabled]]
[[disable]]
[[shutdown]]

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
| `selectionManager` | `SelectionManager` | The manager to read corner positions from |

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
