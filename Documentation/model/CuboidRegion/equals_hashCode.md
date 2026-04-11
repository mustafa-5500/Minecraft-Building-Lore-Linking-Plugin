# equals / hashCode

## Signatures
```java
@Override
public boolean equals(Object obj)

@Override
public int hashCode()
```

## Description
Two `CuboidRegion` instances are equal if they have the same world name and identical min/max coordinates. `hashCode` is consistent with `equals`, computed from all seven fields.

## Parameters (equals)
| Name | Type | Description |
|------|------|-------------|
| `obj` | `Object` | The object to compare |

## Returns
- `equals`: `boolean` — `true` if both regions define the same cuboid in the same world.
- `hashCode`: `int` — hash derived from `worldName`, `minX`, `minY`, `minZ`, `maxX`, `maxY`, `maxZ`.
