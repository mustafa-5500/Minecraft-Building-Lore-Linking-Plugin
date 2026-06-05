# BlockDataExporter — Software Detailed Design

> **API Documentation:** [BlockDataExporter.md](./BlockDataExporter.md)  
> **Source File:** [BlockDataExporter.java](../../src/main/java/org/almond/buildinglore/serializer/BlockDataExporter.java)

---

## 1. Overview

`BlockDataExporter` reads actual block data from a live Minecraft world within a [`Selection`](../model/Selection.md)'s regions and produces structured text output suitable for model training or documentation. It provides both in-memory string export and direct file export capabilities.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.serializer;
```

```java
import org.almond.buildinglore.model.CuboidRegion;
import org.almond.buildinglore.model.Selection;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
```

| Import | Purpose |
|--------|---------|
| [`CuboidRegion`](../model/CuboidRegion.md) | Region boundaries for iteration |
| [`Selection`](../model/Selection.md) | The selection to export |
| `World` | Bukkit world to read blocks from |
| `Block` | Individual block access |
| `BlockData` | Block state information (e.g., door facing, slab type) |
| `File` | Output directory/file paths |
| `FileWriter` | Character-based file output |
| `IOException` | File I/O exception handling |
| `PrintWriter` | Buffered writer with convenience methods |

---

## 3. Class Declaration

```java
/**
 * Reads actual block data from the world within a Selection's regions
 * and outputs structured text for model training.
 */
public class BlockDataExporter {
```

This is a utility class with only `static` methods — it's never instantiated.

---

## 4. `export(Selection, World, boolean)` — In-Memory Export

```java
public static String export(Selection selection, World world, boolean skipAir) {
    StringBuilder sb = new StringBuilder();
```

Builds the entire output in memory using a `StringBuilder` for efficiency.

### 4.1 Header Section

```java
    sb.append("# Selection: ").append(selection.getName()).append('\n');
    sb.append("# World: ").append(selection.getWorldName()).append('\n');
    sb.append("# Regions: ").append(selection.getRegionCount()).append('\n');
    sb.append("# Total Volume: ").append(selection.getTotalVolume()).append('\n');
    sb.append("# Format: x,y,z | block_type | [block_state]\n");
    sb.append('\n');
```

Writes a comment-style header with metadata:
- Selection name for identification.
- World name for context.
- Region count and total volume for statistics.
- Format description line documenting the column structure.
- Blank line separator.

### 4.2 Region Iteration

```java
    for (int idx = 0; idx < selection.getRegions().size(); idx++) {
        CuboidRegion region = selection.getRegions().get(idx);
        sb.append("## Region ").append(idx).append(": ").append(region.toString()).append('\n');
```

Each region gets a sub-header with its index and coordinate range.

### 4.3 Block Iteration (Triple Nested Loop)

```java
        for (int x = region.getMinX(); x <= region.getMaxX(); x++) {
            for (int y = region.getMinY(); y <= region.getMaxY(); y++) {
                for (int z = region.getMinZ(); z <= region.getMaxZ(); z++) {
                    Block block = world.getBlockAt(x, y, z);
```

Iterates over every block position in the region. The order is X → Y → Z (column-major within each XZ column).

`world.getBlockAt(x, y, z)` — Bukkit API call that must execute on the **main server thread**.

### 4.4 Air Skipping

```java
                    if (skipAir && block.getType().isAir()) continue;
```

When `skipAir` is `true`, air blocks (`AIR`, `CAVE_AIR`, `VOID_AIR`) are skipped. This significantly reduces output size for structures in open areas.

### 4.5 Block Data Extraction

```java
                    BlockData data = block.getBlockData();
                    String type = block.getType().getKey().toString();
                    String stateStr = data.getAsString(true);
```

- `getBlockData()` — returns the full block state (material + properties).
- `getType().getKey().toString()` — produces the namespaced type, e.g., `"minecraft:oak_planks"`.
- `getAsString(true)` — returns the full string representation including block states, e.g., `"minecraft:oak_door[facing=east,half=lower,hinge=left,open=false,powered=false]"`.

### 4.6 State Extraction

```java
                    String state = "";
                    int bracketIdx = stateStr.indexOf('[');
                    if (bracketIdx >= 0) {
                        state = stateStr.substring(bracketIdx);
                    }
```

Extracts only the state portion (the `[...]` part) from the full string. Simple blocks without states (e.g., `minecraft:stone`) have no brackets, resulting in an empty `state`.

### 4.7 Output Line

```java
                    sb.append(x).append(',').append(y).append(',').append(z);
                    sb.append(" | ").append(type);
                    if (!state.isEmpty()) {
                        sb.append(" | ").append(state);
                    }
                    sb.append('\n');
```

Produces lines in the format:
```
100,64,200 | minecraft:oak_planks
100,65,200 | minecraft:oak_door | [facing=east,open=false]
```

The state column is omitted for blocks without special states.

### 4.8 Region Separator

```java
            }
        }
        sb.append('\n');
    }
    return sb.toString();
}
```

A blank line between regions for readability. Returns the complete string.

---

## 5. `exportToFile(Selection, World, File, boolean)` — File Export

```java
public static File exportToFile(Selection selection, World world, File exportDir, boolean skipAir) throws IOException {
    if (!exportDir.exists()) {
        exportDir.mkdirs();
    }
    File file = new File(exportDir, selection.getName() + ".txt");
    try (PrintWriter writer = new PrintWriter(new FileWriter(file))) {
        writer.write(export(selection, world, skipAir));
    }
    return file;
}
```

1. **Directory creation** — `mkdirs()` creates the full directory path if it doesn't exist.
2. **File naming** — uses the selection name as the filename with `.txt` extension.
3. **Write** — calls `export(...)` to generate the string, writes it via a `PrintWriter` wrapped around `FileWriter`.
4. **Try-with-resources** — ensures the writer is closed even if an exception occurs.
5. **Return** — returns the `File` object so the caller can report the path.
6. **Throws IOException** — propagated to the caller for handling (command reports to player).

---

## 6. Output Format Specification

```
# Selection: MyHouse
# World: world
# Regions: 2
# Total Volume: 1500
# Format: x,y,z | block_type | [block_state]

## Region 0: (100,64,200)-(110,70,210)
100,64,200 | minecraft:stone
100,64,201 | minecraft:oak_planks
100,65,200 | minecraft:oak_door | [facing=east,half=lower,hinge=left,open=false,powered=false]
...

## Region 1: (111,64,200)-(115,70,210)
111,64,200 | minecraft:cobblestone
...
```

---

## 7. Performance Characteristics

| Factor | Impact |
|--------|--------|
| Block access | O(V) where V = total volume across all regions |
| Memory | Entire output buffered in StringBuilder |
| Thread requirement | Must run on Bukkit main thread (synchronous) |
| Disk I/O | Single buffered write at the end |

For a 100×100×100 selection (1,000,000 blocks), this could produce several MB of text and take noticeable time. The command handler warns the player accordingly.

---

## 8. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Static utility methods | No instance state needed; pure function of inputs |
| `skipAir` parameter | Most use cases don't need millions of air block entries |
| Pipe-delimited format | Easy to parse; human-readable; compatible with model training pipelines |
| State extracted via string manipulation | Avoids relying on Bukkit internals; `getAsString(true)` is the stable public API |
| Synchronous execution | Bukkit `World.getBlockAt()` must be called from the main thread |
| `StringBuilder` for in-memory export | Efficient string concatenation; single allocation at `toString()` |
| Separate file export method | Allows reuse of the core export logic for other output targets |
