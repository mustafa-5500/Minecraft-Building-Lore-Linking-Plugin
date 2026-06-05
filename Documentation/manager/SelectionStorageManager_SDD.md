# SelectionStorageManager — Software Detailed Design

> **API Documentation:** [SelectionStorageManager.md](./SelectionStorageManager.md)  
> **Source File:** [SelectionStorageManager.java](../../src/main/java/org/almond/buildinglore/manager/SelectionStorageManager.java)

---

## 1. Overview

`SelectionStorageManager` is the persistence layer for [`Selection`](../model/Selection.md) objects. It reads and writes YAML files under `plugins/BuildingLore/selections/<player-uuid>/` and maintains an in-memory cache for fast repeated access. Each selection is stored as a single `.yml` file named after the selection.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.manager;
```

```java
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.logging.Level;

import org.almond.buildinglore.model.CuboidRegion;
import org.almond.buildinglore.model.LoreDocument;
import org.almond.buildinglore.model.Selection;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.plugin.java.JavaPlugin;
```

| Import | Purpose |
|--------|---------|
| `File`, `IOException` | Filesystem operations |
| `ArrayList`, `HashMap`, `List`, `Map`, `UUID` | Collections and identifiers |
| `Level` | Java logging level constants |
| [`CuboidRegion`](../model/CuboidRegion.md), [`LoreDocument`](../model/LoreDocument.md), [`Selection`](../model/Selection.md) | Domain model classes |
| `ConfigurationSection`, `YamlConfiguration` | Bukkit's YAML configuration API |
| `JavaPlugin` | Access to plugin data folder and logger |

---

## 3. Class Declaration

```java
/**
 * Persists Selections as YAML files under plugins/BuildingLore/selections/<player-uuid>/.
 */
public class SelectionStorageManager {
```

---

## 4. Instance Fields

```java
private final File selectionsDir;
private final JavaPlugin plugin;
private final Map<UUID, Map<String, Selection>> cache = new HashMap<>();
```

| Field | Type | Purpose |
|-------|------|---------|
| `selectionsDir` | `File` | Root directory: `plugins/BuildingLore/selections/` |
| `plugin` | `JavaPlugin` | Access to `getDataFolder()` and `getLogger()` |
| `cache` | `Map<UUID, Map<String, Selection>>` | Two-level cache: player UUID → selection name → [`Selection`](../model/Selection.md) object |

The cache is eagerly populated on reads and updated on writes/deletes. It serves as a write-through cache.

---

## 5. Constructor

```java
public SelectionStorageManager(JavaPlugin plugin) {
    this.plugin = plugin;
    this.selectionsDir = new File(plugin.getDataFolder(), "selections");
    if (!selectionsDir.exists()) {
        selectionsDir.mkdirs();
    }
}
```

1. Stores the plugin reference.
2. Resolves the selections directory path relative to the plugin's data folder.
3. Creates the directory (including parents) if it doesn't exist. `mkdirs()` is idempotent.

---

## 6. `saveSelection(Selection)`

```java
public void saveSelection(Selection selection) {
    File playerDir = new File(selectionsDir, selection.getOwner().toString());
    if (!playerDir.exists()) {
        playerDir.mkdirs();
    }
    File file = new File(playerDir, selection.getName() + ".yml");
```

Resolves the file path: `selections/<owner-uuid>/<name>.yml`.

```java
    YamlConfiguration config = new YamlConfiguration();
    config.set("id", selection.getId().toString());
    config.set("name", selection.getName());
    config.set("owner", selection.getOwner().toString());
    config.set("world", selection.getWorldName());
    config.set("createdAt", selection.getCreatedAt());
```

Writes scalar fields to the YAML structure. UUIDs are stored as strings.

```java
    List<String> regionStrings = new ArrayList<>();
    for (CuboidRegion region : selection.getRegions()) {
        regionStrings.add(region.toString());
    }
    config.set("regions", regionStrings);
```

Regions are serialized using `CuboidRegion.toString()` which produces `(x1,y1,z1)-(x2,y2,z2)` format. Stored as a YAML string list.

```java
    // Save lore documents
    for (Map.Entry<String, LoreDocument> entry : selection.getLoreDocuments().entrySet()) {
        LoreDocument doc = entry.getValue();
        String path = "lore." + doc.getName();
        config.set(path + ".id", doc.getId().toString());
        config.set(path + ".createdAt", doc.getCreatedAt());
        config.set(path + ".entries", doc.getEntries());
    }
```

Each lore document is stored under `lore.<docName>` with its UUID, timestamp, and string list of entries.

```java
    try {
        config.save(file);
    } catch (IOException e) {
        plugin.getLogger().log(Level.SEVERE, "Failed to save selection " + selection.getName(), e);
    }
```

Writes the YAML to disk. Logs at SEVERE level if the write fails (disk full, permissions, etc.).

```java
    cache.computeIfAbsent(selection.getOwner(), k -> new HashMap<>()).put(selection.getName(), selection);
}
```

Updates the in-memory cache. `computeIfAbsent` creates the player's map if it doesn't exist yet.

---

## 7. `loadSelection(UUID, String)`

```java
public Selection loadSelection(UUID owner, String name) {
    Map<String, Selection> playerCache = cache.get(owner);
    if (playerCache != null && playerCache.containsKey(name)) {
        return playerCache.get(name);
    }

    File file = new File(selectionsDir, owner.toString() + File.separator + name + ".yml");
    if (!file.exists()) return null;

    return loadFromFile(file, owner);
}
```

**Cache-first strategy:**
1. Check the in-memory cache for an existing entry.
2. If not cached, resolve the file path.
3. If file doesn't exist, return `null`.
4. Otherwise delegate to `loadFromFile` which parses the YAML and populates the cache.

---

## 8. `loadAllForPlayer(UUID)`

```java
public List<Selection> loadAllForPlayer(UUID owner) {
    Map<String, Selection> playerCache = cache.get(owner);
    if (playerCache != null && !playerCache.isEmpty()) {
        return new ArrayList<>(playerCache.values());
    }

    List<Selection> result = new ArrayList<>();
    File playerDir = new File(selectionsDir, owner.toString());
    if (!playerDir.exists() || !playerDir.isDirectory()) return result;

    File[] files = playerDir.listFiles((dir, fileName) -> fileName.endsWith(".yml"));
    if (files == null) return result;

    for (File file : files) {
        Selection sel = loadFromFile(file, owner);
        if (sel != null) {
            result.add(sel);
        }
    }
    return result;
}
```

1. Returns cached values if the player's cache is non-empty.
2. Lists all `.yml` files in the player's directory using a filename filter.
3. Loads each file individually, skipping any that fail to parse.
4. Each successful load updates the cache (inside `loadFromFile`).

---

## 9. `deleteSelection(UUID, String)`

```java
public boolean deleteSelection(UUID owner, String name) {
    File file = new File(selectionsDir, owner.toString() + File.separator + name + ".yml");
    boolean deleted = file.exists() && file.delete();

    Map<String, Selection> playerCache = cache.get(owner);
    if (playerCache != null) {
        playerCache.remove(name);
    }
    return deleted;
}
```

1. Resolves the file path.
2. Attempts to delete the file — returns `false` if it didn't exist or deletion failed.
3. Removes from cache regardless (idempotent).
4. Returns whether the file was actually deleted.

---

## 10. `getSelection(UUID, String)`

```java
public Selection getSelection(UUID owner, String name) {
    return loadSelection(owner, name);
}
```

A convenience alias for `loadSelection`. Used throughout the codebase as the primary accessor.

---

## 11. `loadFromFile(File, UUID)` — Private

```java
private Selection loadFromFile(File file, UUID owner) {
    YamlConfiguration config = YamlConfiguration.loadConfiguration(file);
    try {
        UUID id = UUID.fromString(config.getString("id"));
        String name = config.getString("name");
        String world = config.getString("world");
        long createdAt = config.getLong("createdAt");
```

Loads the YAML file using Bukkit's `YamlConfiguration.loadConfiguration` (handles encoding, returns empty config on parse error). Extracts scalar fields.

```java
        List<CuboidRegion> regions = new ArrayList<>();
        List<String> regionStrings = config.getStringList("regions");
        for (String regionStr : regionStrings) {
            regions.add(CuboidRegion.fromString(world, regionStr));
        }
```

Parses each region string (format: `(x1,y1,z1)-(x2,y2,z2)`) back into [`CuboidRegion`](../model/CuboidRegion.md) objects using the static factory method. The world name is passed in since it's not part of the compact format.

```java
        Selection selection = new Selection(id, name, owner, world, regions, createdAt);
```

Constructs the [`Selection`](../model/Selection.md) with the full constructor (ID, name, owner, world, pre-built regions list, timestamp).

```java
        // Load lore documents
        ConfigurationSection loreSection = config.getConfigurationSection("lore");
        if (loreSection != null) {
            for (String docName : loreSection.getKeys(false)) {
                ConfigurationSection docSection = loreSection.getConfigurationSection(docName);
                if (docSection != null) {
                    UUID docId = UUID.fromString(docSection.getString("id"));
                    long docCreatedAt = docSection.getLong("createdAt");
                    List<String> entries = docSection.getStringList("entries");
                    LoreDocument doc = new LoreDocument(docId, docName, entries, docCreatedAt);
                    selection.addLoreDocument(doc);
                }
            }
        }
```

Iterates over each key under the `lore` section. Each key is a document name containing `id`, `createdAt`, and `entries`. Reconstructs [`LoreDocument`](../model/LoreDocument.md) objects and attaches them to the selection.

```java
        cache.computeIfAbsent(owner, k -> new HashMap<>()).put(name, selection);
        return selection;
    } catch (Exception e) {
        plugin.getLogger().log(Level.WARNING, "Failed to load selection from " + file.getName(), e);
        return null;
    }
}
```

- Populates the cache on successful load.
- Catches any exception (malformed UUID, missing fields, parse errors) and logs a warning.
- Returns `null` on failure — callers handle this gracefully.

---

## 12. File Layout

```
plugins/BuildingLore/
  selections/
    <player-uuid-1>/
      MyHouse.yml
      Bridge.yml
    <player-uuid-2>/
      Tower.yml
```

### Example YAML Content

```yaml
id: "550e8400-e29b-41d4-a716-446655440000"
name: "MyHouse"
owner: "f47ac10b-58cc-4372-a567-0e02b2c3d479"
world: "world"
createdAt: 1716000000000
regions:
  - "(100,64,200)-(110,70,210)"
  - "(111,64,200)-(115,70,210)"
lore:
  History:
    id: "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    createdAt: 1716000001000
    entries:
      - "Built in the first week of the server."
      - "Originally a small hut, expanded over time."
```

---

## 13. Design Decisions

| Decision | Rationale |
|----------|-----------|
| YAML format (via `YamlConfiguration`) | Native Bukkit support; human-readable/editable; no external dependencies |
| One file per selection | Avoids locking issues; allows independent save/delete operations |
| Write-through cache | Reads are fast (O(1) map lookup); writes always hit disk for durability |
| `computeIfAbsent` for lazy cache init | Avoids pre-allocating maps for all possible players |
| Region stored as compact string | Compact on disk; single-line per region in YAML list |
| Broad catch in `loadFromFile` | Corrupted files shouldn't crash the plugin; logged and skipped |
| Synchronous I/O | Acceptable for small YAML files; avoids async complexity |
