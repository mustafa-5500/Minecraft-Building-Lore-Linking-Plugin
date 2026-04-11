# exportToFile

## Signature
```java
public static File exportToFile(Selection selection, World world, File exportDir, boolean skipAir) throws IOException
```

## Description
Convenience method that calls `export()` and writes the result to a text file at `<exportDir>/<selection-name>.txt`. Creates the directory if needed.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | `Selection` | The selection to export |
| `world` | `World` | The Bukkit World |
| `exportDir` | `File` | Target directory for the output file |
| `skipAir` | `boolean` | If `true`, air blocks are omitted |

## Returns
`File` — the written output file.

## Throws
`IOException` — if the file cannot be written.
