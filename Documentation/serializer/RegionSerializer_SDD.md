# RegionSerializer — Software Detailed Design

> **API Documentation:** [RegionSerializer.md](./RegionSerializer.md)  
> **Source File:** [RegionSerializer.java](../../src/main/java/org/almond/buildinglore/serializer/RegionSerializer.java)

---

## 1. Overview

`RegionSerializer` converts `Selection` objects to and from compact text tokens that players can copy-paste to share selections. The token format encodes the world name and all region coordinates into a single-line string.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.serializer;
```

```java
import org.almond.buildinglore.model.CuboidRegion;
import org.almond.buildinglore.model.Selection;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
```

| Import | Purpose |
|--------|---------|
| `CuboidRegion` | Region data to encode/decode |
| `Selection` | The object being serialized/deserialized |
| `ArrayList`, `List` | Building the region list during deserialization |
| `UUID` | Generating a new UUID for imported selections |

---

## 3. Class Declaration & Javadoc

```java
/**
 * Converts a Selection to/from a compact text token for embedding in documents.
 *
 * Format: [BL:world_name|x1,y1,z1>x2,y2,z2|x3,y3,z3>x4,y4,z4]
 */
public class RegionSerializer {
```

The token format documentation is embedded in the class Javadoc.

---

## 4. Token Format Specification

```
[BL:<world_name>|<region_1>|<region_2>|...|<region_n>]
```

Where each `<region>` is:
```
minX,minY,minZ>maxX,maxY,maxZ
```

**Example:**
```
[BL:world|100,64,200>110,70,210|111,64,200>115,70,210]
```

| Component | Delimiter | Purpose |
|-----------|-----------|---------|
| `[BL:` | Prefix | Identifies this as a BuildingLore token |
| `]` | Suffix | Marks the end of the token |
| `|` | Pipe | Separates world name from regions, and regions from each other |
| `,` | Comma | Separates X, Y, Z coordinates |
| `>` | Greater-than | Separates min corner from max corner within a region |

---

## 5. `serialize(Selection)` — Encoding

```java
public static String serialize(Selection selection) {
    StringBuilder sb = new StringBuilder();
    sb.append("[BL:").append(selection.getWorldName());
```

Starts building the token with the prefix and world name.

```java
    for (CuboidRegion region : selection.getRegions()) {
        sb.append('|');
        sb.append(region.getMinX()).append(',').append(region.getMinY()).append(',').append(region.getMinZ());
        sb.append('>');
        sb.append(region.getMaxX()).append(',').append(region.getMaxY()).append(',').append(region.getMaxZ());
    }
```

For each region:
1. Pipe delimiter before the region data.
2. Min coordinates (X, Y, Z) separated by commas.
3. `>` separator.
4. Max coordinates (X, Y, Z) separated by commas.

```java
    sb.append(']');
    return sb.toString();
}
```

Closes the token with `]` and returns the complete string.

**Output example:** `[BL:world|100,64,200>110,70,210|111,64,200>115,70,210]`

---

## 6. `deserialize(String, UUID)` — Decoding

```java
public static Selection deserialize(String token, UUID owner) {
```

The `owner` parameter must be provided separately because it's not embedded in the token (security consideration — prevents impersonation).

### 6.1 Format Validation

```java
    if (token == null || !token.startsWith("[BL:") || !token.endsWith("]")) {
        throw new IllegalArgumentException("Invalid BL token format");
    }
```

Validates the prefix and suffix. Null check prevents NPE.

### 6.2 Strip Wrapper

```java
    String inner = token.substring(4, token.length() - 1);
```

Removes `[BL:` (4 chars) from the front and `]` (1 char) from the back, leaving just `world_name|region|region|...`.

### 6.3 Split by Pipe

```java
    String[] parts = inner.split("\\|");
    if (parts.length < 1) {
        throw new IllegalArgumentException("Invalid BL token: missing world name");
    }
```

Splits on `|` (escaped as `\\|` since `split` takes a regex). The first element is always the world name.

### 6.4 Extract World Name

```java
    String worldName = parts[0];
    List<CuboidRegion> regions = new ArrayList<>();
```

### 6.5 Parse Each Region

```java
    for (int i = 1; i < parts.length; i++) {
        String regionStr = parts[i];
        String[] corners = regionStr.split(">");
        if (corners.length != 2) {
            throw new IllegalArgumentException("Invalid region in BL token: " + regionStr);
        }
        String[] min = corners[0].split(",");
        String[] max = corners[1].split(",");
        if (min.length != 3 || max.length != 3) {
            throw new IllegalArgumentException("Invalid coordinates in BL token: " + regionStr);
        }
        regions.add(new CuboidRegion(
            worldName,
            Integer.parseInt(min[0].trim()), Integer.parseInt(min[1].trim()), Integer.parseInt(min[2].trim()),
            Integer.parseInt(max[0].trim()), Integer.parseInt(max[1].trim()), Integer.parseInt(max[2].trim())
        ));
    }
```

For each region segment (indices 1..n):
1. Split on `>` to get min and max halves.
2. Validate exactly 2 parts.
3. Split each half on `,` to get 3 coordinates.
4. Validate exactly 3 coordinates per half.
5. Parse integers with `trim()` for whitespace tolerance.
6. Construct `CuboidRegion` (constructor handles min/max normalization).

Throws `IllegalArgumentException` with descriptive messages for any validation failure. `Integer.parseInt` will also throw `NumberFormatException` (subclass of `IllegalArgumentException`) for non-numeric values.

### 6.6 Construct Selection

```java
    return new Selection(UUID.randomUUID(), "imported", owner, worldName, regions, System.currentTimeMillis());
}
```

Creates a new `Selection` with:
- **Random UUID** — unique identity for the imported selection.
- **Name `"imported"`** — default name; player can see it in their list.
- **Provided `owner`** — the importing player becomes the owner.
- **Parsed `worldName`** — from the token.
- **Parsed `regions`** — all decoded regions.
- **Current timestamp** — marks the import time.

---

## 7. Error Handling

| Error Condition | Exception | Message |
|-----------------|-----------|---------|
| Null or missing prefix/suffix | `IllegalArgumentException` | "Invalid BL token format" |
| Empty token body | `IllegalArgumentException` | "Invalid BL token: missing world name" |
| Region without `>` separator | `IllegalArgumentException` | "Invalid region in BL token: ..." |
| Wrong coordinate count | `IllegalArgumentException` | "Invalid coordinates in BL token: ..." |
| Non-numeric coordinate | `NumberFormatException` | (from `Integer.parseInt`) |

All exceptions are caught by `BuildingLoreCommand.handleImport` and reported to the player.

---

## 8. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Static utility methods | No instance state; pure transformation functions |
| `[BL:...]` wrapper | Makes tokens easily recognizable and prevents accidental parsing of arbitrary text |
| Owner not in token | Security: prevents forging selections as other players |
| Fixed name `"imported"` | Simple convention; player can identify imports in their list |
| `trim()` on coordinates | Tolerance for copy-paste artifacts (trailing spaces) |
| `IllegalArgumentException` for all errors | Consistent exception type; caught uniformly by the command handler |
| `>` as corner separator | Avoids conflict with `-` which appears in negative coordinates |
