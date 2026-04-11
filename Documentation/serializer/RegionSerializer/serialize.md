# serialize

## Signature
```java
public static String serialize(Selection selection)
```

## Description
Converts a `Selection` into a compact text token in the format:
```
[BL:world_name|minX,minY,minZ>maxX,maxY,maxZ|...]
```
Each region is separated by `|`. Designed to be copy-pasted into documents.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | `Selection` | The selection to serialize |

## Returns
`String` — the compact token.
