# subtract

## Signature
```java
public Set<CuboidRegion> subtract(CuboidRegion other)
```

## Description
Subtracts another region from this one, returning the set of remaining cuboid pieces. If there is no overlap, returns a set containing only this region. Splits along all three axes (up to 6 remaining pieces).

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The region to subtract |

## Returns
`Set<CuboidRegion>` — the remaining cuboid fragments after subtraction.
