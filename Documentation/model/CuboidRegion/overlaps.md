# overlaps

## Signature
```java
public boolean overlaps(CuboidRegion other)
```

## Description
Checks if this region overlaps (shares any block coordinates) with another region. Regions in different worlds never overlap.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The other region to test against |

## Returns
`boolean` — `true` if the two regions share at least one block coordinate.
