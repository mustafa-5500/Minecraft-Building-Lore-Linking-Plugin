# export

## Signature
```java
public static String export(Selection selection, World world, boolean skipAir)
```

## Description
Reads every block in each region of the selection from the world and produces structured text output. Each line contains position, block type, and optional block state. Includes a header with selection metadata.

## Output Format
```
x,y,z | minecraft:block_type | [state=value,...]
```

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | `Selection` | The selection to export |
| `world` | `World` | The Bukkit World to read blocks from |
| `skipAir` | `boolean` | If `true`, air blocks are omitted |

## Returns
`String` — the full block data text.
