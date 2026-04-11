# isAdjacentTo

## Signature
```java
public boolean isAdjacentTo(CuboidRegion other)
```

## Description
Checks if this region is adjacent (touching face-to-face, with no gap and no overlap) to another region. Tests all three axes. Regions must be in the same world.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The other region to test against |

## Returns
`boolean` — `true` if the regions share a face along any axis.
