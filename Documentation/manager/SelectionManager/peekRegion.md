# peekRegion

## Signature
```java
public CuboidRegion peekRegion(UUID playerId)
```

## Description
Returns what the region would be from the current corners without consuming/clearing them. Useful for previewing the selection volume.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

## Returns
`CuboidRegion` or `null`.
