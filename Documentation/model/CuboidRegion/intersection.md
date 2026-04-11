# intersection

## Signature
```java
public CuboidRegion intersection(CuboidRegion other)
```

## Description
Calculates the overlapping sub-region shared by this region and another. Returns `null` if the regions do not overlap.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The other region to intersect with |

## Returns
`CuboidRegion` or `null` — the intersection cuboid, or `null` if no overlap exists.
