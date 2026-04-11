# getCorner1 / getCorner2

## Signatures
```java
public Location getCorner1(UUID playerId)
public Location getCorner2(UUID playerId)
```

## Description
Retrieves the stored corner location for a player. Returns `null` if the corner has not been set.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

## Returns
`Location` or `null`.
