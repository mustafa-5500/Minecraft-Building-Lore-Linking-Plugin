# BlockDataExporter.java
[[BlockDataExporter.java]]

Reads actual block data from the Bukkit world within a `Selection`'s regions and outputs structured text suitable for model training. Each block is recorded with its coordinates, type, and block state. Air blocks can optionally be skipped.

**Functions:**
[[export]]
[[exportToFile]]

---

## export

### Signature
```java
public static String export(Selection selection, World world, boolean skipAir)
```

### Description
Reads every block in each region of the selection from the world and produces structured text output. Each line contains position, block type, and optional block state. Includes a header with selection metadata.

### Output Format
```
x,y,z | minecraft:block_type | [state=value,...]
```

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | `Selection` | The selection to export |
| `world` | `World` | The Bukkit World to read blocks from |
| `skipAir` | `boolean` | If `true`, air blocks are omitted |

### Returns
`String` — the full block data text.

---

## exportToFile

### Signature
```java
public static File exportToFile(Selection selection, World world, File exportDir, boolean skipAir) throws IOException
```

### Description
Convenience method that calls `export()` and writes the result to a text file at `<exportDir>/<selection-name>.txt`. Creates the directory if needed.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | `Selection` | The selection to export |
| `world` | `World` | The Bukkit World |
| `exportDir` | `File` | Target directory for the output file |
| `skipAir` | `boolean` | If `true`, air blocks are omitted |

### Returns
`File` — the written output file.

### Throws
`IOException` — if the file cannot be written.
