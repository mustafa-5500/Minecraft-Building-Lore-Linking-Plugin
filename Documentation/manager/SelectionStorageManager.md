# SelectionStorageManager.java
[[SelectionStorageManager.java]]

Persists `Selection` objects as YAML files under `plugins/BuildingLore/selections/<player-uuid>/`. Maintains an in-memory cache keyed by owner UUID and selection name for fast lookups, with disk I/O for durability.

**Fields:**
- `selectionsDir` — Root directory for all selection YAML files
- `plugin` — Reference to the owning `JavaPlugin` instance
- `cache` — In-memory cache mapping owner UUID → (selection name → Selection)

**Functions:**
[[constructor]]
[[saveSelection]]
[[loadSelection]]
[[loadAllForPlayer]]
[[deleteSelection]]
[[getSelection]]
[[loadFromFile]]

---

## SelectionStorageManager (Constructor)

### Signature
```java
public SelectionStorageManager(JavaPlugin plugin)
```

### Description
Initializes the storage manager. Creates the `plugins/BuildingLore/selections/` directory if it doesn't exist. Sets up the in-memory cache.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `plugin` | `JavaPlugin` | The owning plugin instance (used for data folder and logging) |

---

## saveSelection

### Signature
```java
public void saveSelection(Selection selection)
```

### Description
Persists a selection to disk as a YAML file at `selections/<owner-uuid>/<name>.yml`. Also updates the in-memory cache. Region data is stored as compact string representations.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | `Selection` | The selection to save |

### Returns
`void`

---

## loadSelection

### Signature
```java
public Selection loadSelection(UUID owner, String name)
```

### Description
Loads a single selection by owner and name. Checks the in-memory cache first; if not cached, reads from disk.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `owner` | `UUID` | Player UUID |
| `name` | `String` | Selection name |

### Returns
`Selection` or `null` — the loaded selection, or `null` if not found.

---

## loadAllForPlayer

### Signature
```java
public List<Selection> loadAllForPlayer(UUID owner)
```

### Description
Loads all saved selections for a player. Returns from cache if available, otherwise reads all `.yml` files in the player's selection directory.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `owner` | `UUID` | Player UUID |

### Returns
`List<Selection>` — all selections belonging to the player (empty list if none).

---

## deleteSelection

### Signature
```java
public boolean deleteSelection(UUID owner, String name)
```

### Description
Deletes a selection's YAML file from disk and removes it from the in-memory cache.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `owner` | `UUID` | Player UUID |
| `name` | `String` | Selection name |

### Returns
`boolean` — `true` if the file existed and was deleted.

---

## getSelection

### Signature
```java
public Selection getSelection(UUID owner, String name)
```

### Description
Convenience method that delegates to `loadSelection`. Returns a selection from cache or disk.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `owner` | `UUID` | Player UUID |
| `name` | `String` | Selection name |

### Returns
`Selection` or `null`.

---

## loadFromFile

### Signature
```java
private Selection loadFromFile(File file, UUID owner)
```

### Description
Internal method that reads a YAML file and reconstructs a `Selection` object. Parses the id, name, world, timestamp, and region strings. Caches the result. Logs a warning on failure.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `file` | `File` | The YAML file to read |
| `owner` | `UUID` | The owning player's UUID |

### Returns
`Selection` or `null` — the parsed selection, or `null` if parsing failed.
