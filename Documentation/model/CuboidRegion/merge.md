# merge

## Signature
```java
public CuboidRegion merge(CuboidRegion other)
```

## Description
Merges this region with another by producing the bounding box union (the smallest cuboid that contains both regions).

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `other` | `CuboidRegion` | The region to merge with |

## Returns
`CuboidRegion` — a new region representing the bounding box of both inputs.
