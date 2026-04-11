# isSamePlaneAs

## Signature
```java
public boolean isSamePlaneAs(CuboidRegion other)
```

## Description
Checks if two regions share the same extents along two of the three axes, meaning they could be merged into a single cuboid along the remaining axis.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The other region to compare |

## Returns
`boolean` — `true` if the regions are coplanar along two axes.
