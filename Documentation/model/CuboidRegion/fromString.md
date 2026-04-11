# fromString

## Signature
```java
public static CuboidRegion fromString(String worldName, String s)
```

## Description
Parses a compact string (produced by `toString()`) back into a `CuboidRegion`. Expected format: `(x1,y1,z1)-(x2,y2,z2)`.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `worldName` | `String` | The world to associate the region with |
| `s` | `String` | The string to parse |

## Returns
`CuboidRegion` — the parsed region.
