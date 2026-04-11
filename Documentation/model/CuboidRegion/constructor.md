# CuboidRegion (Constructor)

## Signature
```java
public CuboidRegion(String worldName, int x1, int y1, int z1, int x2, int y2, int z2)
```

## Description
Creates a cuboid region from two arbitrary corner positions. The coordinates are automatically normalized so that `min` values are always less than or equal to `max` values.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `worldName` | `String` | The name of the world this region belongs to |
| `x1` | `int` | X coordinate of the first corner |
| `y1` | `int` | Y coordinate of the first corner |
| `z1` | `int` | Z coordinate of the first corner |
| `x2` | `int` | X coordinate of the second corner |
| `y2` | `int` | Y coordinate of the second corner |
| `z2` | `int` | Z coordinate of the second corner |

## Returns
A new `CuboidRegion` instance.
